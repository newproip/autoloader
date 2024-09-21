from enum import IntEnum
from threading import Thread
from time import sleep

from newpro_autoloader.axis_status import AxisStatus, LoaderType, MainStatus, OverallSystemStatus
from newpro_autoloader.device_error import DeviceError
from newpro_autoloader.loader_connection import LoaderCommand, LoaderConnection

PORT_NUMBER = 1234
PORT_NUMBER_STATUS = 1235

RESPONSE_BODY_OFFSET = 3
SIZE_OF_ACTION_NAME = 32

EVAC_TIMEOUT = 15
HOME_TIMEOUT = 60
LOAD_TIMEOUT = 180

class Axis(IntEnum):
    Elevator = 0,
    Loader = 1,
    All = 2,

class SlotState(IntEnum):
    Absent = 0,
    Present = 1,
    Unknown = 2,

class Loader:

    def _updater(self):
        try:
            while self._run_thread:
                self._get_status()
                sleep(0.5)
        except Exception as ex:
            print(ex)

    def __init__(self,
                 address: str = "autoloader",
                 fallback_address: str = "192.168.0.9"):
        """Create a loader interface."""

        self._addresses = [address, fallback_address]
        self._connection: LoaderConnection = LoaderConnection(self._addresses, PORT_NUMBER)
        self._status_connection: LoaderConnection = LoaderConnection(self._addresses, PORT_NUMBER_STATUS)
        self._update_thread = Thread(target=self._updater, name="Update thread", daemon=True)
        self._run_thread = False

        self._elevator_status: AxisStatus = AxisStatus()
        self._loader_status: AxisStatus = AxisStatus()
        self._main_status: MainStatus = MainStatus()

        self._version, self._sub_version, self._number_of_slots = self.get_version()
        self._get_status()
    
    def __enter__(self):
        self._run_thread = True
        self._update_thread.start()
        return self
    
    def __exit__(self, *args):
        self._run_thread = False

    @property
    def number_of_slots(self) -> int:
        return self._number_of_slots
    
    @property
    def version(self) -> int:
        return self._version
    
    @property
    def sub_version(self) -> int:
        return self._sub_version
    
    @property
    def is_cassette_present(self) -> bool:
        """Return True if a cassette is installed in the loader"""
        return self.slot_state(self.number_of_slots + 1) == SlotState.Present
    
    @property
    def is_gripped(self) -> bool:
        """Return True if the gripper is full"""
        return self._main_status._gripped_from_slot != 0
    
    @property
    def index_loaded(self) -> int | None:
        """This indicates the slot number of the currently gripped payload, if any.
        It does not indicate if the payload is fully loaded into the microscope."""
        slot = self._main_status._gripped_from_slot
        if slot:
            return slot
        else:
            return None
        
    @property
    def is_homed(self) -> bool:
        """This indicates if the homing process has been completed so that
        the positions have been determined.  It does not indicate if the loader
        is presently at the home position."""
        loader_homed: bool = self._loader_status._overall_status & OverallSystemStatus.AbsolutePositionKnown
        elevator_homed: bool = self._elevator_status._overall_status & OverallSystemStatus.AbsolutePositionKnown
        return loader_homed and elevator_homed

    @property
    def last_error(self) -> DeviceError | int:
        try:
            return DeviceError(self._main_status._last_error)
        except IndexError:
            return self._main_status._last_error
        
    @property
    def _loader_type(self) -> LoaderType:
        return LoaderType.Beta if self.version else LoaderType.Alpha
    
    def slot_state(self, slot_number: int) -> SlotState:
        state: bool = self._main_status._slot_state & (1 << slot_number-1) > 0
        known: bool = self._main_status._slot_known & (1 << slot_number-1) > 0
        if known:
            if state:
                return SlotState.Present
            else:
                return SlotState.Absent
        else:
            return SlotState.Unknown

    def _get_status(self):
        resp: bytearray = self._status_connection.command(LoaderCommand.GET_STATUS)
        next_idx = RESPONSE_BODY_OFFSET

        next_idx = self._elevator_status.unpack(resp, next_idx, self._loader_type)
        next_idx = self._loader_status.unpack(resp, next_idx, self._loader_type)
        next_idx = self._main_status.unpack(resp, next_idx)

    def get_version(self) -> tuple[int, int, int]:
        """ Get basic info from the device
        returns:
            version: Main version number  
            sub_version: Sub version number
            number_of_slots: Number of slots currently configured in the loader"""

        response: bytearray = self._connection.command(LoaderCommand.GET_VERSION)
        version = int.from_bytes(response[RESPONSE_BODY_OFFSET:RESPONSE_BODY_OFFSET+2], "little")
        sub_version = int.from_bytes(response[RESPONSE_BODY_OFFSET+2:RESPONSE_BODY_OFFSET+4], "little")
        number_of_slots = int.from_bytes(response[RESPONSE_BODY_OFFSET+4:RESPONSE_BODY_OFFSET+8], "little")

        return version, sub_version, number_of_slots
    
    def home(self, axis: Axis = Axis.All, vacuum_safe: bool = True):
        self._connection.command(
            LoaderCommand.HOME,
            bytearray([axis, vacuum_safe]),
            HOME_TIMEOUT
        )
        self._get_status()
        
    def stop(self, signum = None, frame = None):
        """Immediately stops loader motion/action
        args:
            signum and frame are there so that this can be used
            as an OS signal handler
        """
        self._status_connection.command(LoaderCommand.STOP)

    def load(self, slot_number: int):
        self._connection.command(
            LoaderCommand.LOAD,
            bytearray([slot_number]),
            LOAD_TIMEOUT
        )

    def load_cassette(self, vacuum_safe: bool = True):
        self._connection.command(
            LoaderCommand.LOAD_CASSETTE,
            bytearray([vacuum_safe]),
            LOAD_TIMEOUT
        )
        self._get_status()

    def evac(self):
        self._connection.command(
            LoaderCommand.EVAC,
            timeout=EVAC_TIMEOUT
        )

    def clear_last_error(self):
        self._connection.command(LoaderCommand.CLEAR_LAST_ERROR)
