"""Top-level functions for accessing the autoloader"""
from enum import IntEnum
from threading import Thread
from time import sleep
from typing import Optional, Union

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
    """Which autoloader axis"""
    ELEVATOR = 0
    LOADER = 1
    ALL = 2

class PayloadState(IntEnum):
    """State of payload presence"""
    ABSENT = 0
    PRESENT = 1
    UNKNOWN = 2

class Loader:
    """Top-level class for accessing the autoloader.  Can be used as a context
    manager to maintain the connection resources."""
    def _updater(self):
        try:
            while self._run_thread:
                self._get_status()
                sleep(0.5)
        except Exception as ex:   # pylint: disable=broad-exception-caught
            print(ex)

    def __init__(self,
                 address: str = "autoloader",
                 fallback_address: str = "192.168.0.9"):
        """Create a loader interface."""

        self._addresses = [address, fallback_address]
        self._connection: LoaderConnection = LoaderConnection(self._addresses, PORT_NUMBER)
        self._status_connection: LoaderConnection = LoaderConnection(
            self._addresses,
            PORT_NUMBER_STATUS,
        )
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
        """Number of slots in the cassette"""
        return self._number_of_slots

    @property
    def version(self) -> int:
        """Main version number, indicating Alpha or Beta"""
        return self._version

    @property
    def sub_version(self) -> int:
        """Embedded software version number"""
        return self._sub_version

    @property
    def is_cassette_present(self) -> bool:
        """Return True if a cassette is installed in the loader"""
        return self.slot_state(self.number_of_slots + 1) == PayloadState.PRESENT

    @property
    def is_gripped(self) -> bool:
        """Return True if the gripper is full"""
        return self._main_status.gripped_from_slot != 0

    @property
    def grip_state(self) -> PayloadState:
        """Return the payload state of the gripper"""
        return self.slot_state(self.number_of_slots + 2)

    @property
    def index_loaded(self) -> Optional[int]:
        """This indicates the slot number of the currently gripped payload, if any.
        It does not indicate if the payload is fully loaded into the microscope."""
        slot = self._main_status.gripped_from_slot
        if slot:
            return slot

        return None

    @property
    def is_homed(self) -> bool:
        """This indicates if the homing process has been completed so that
        the positions have been determined.  It does not indicate if the loader
        is presently at the home position."""
        loader_homed: bool = self._loader_status.status & \
            OverallSystemStatus.ABSOLUTE_POSITION_KNOWN
        elevator_homed: bool = self._elevator_status.status & \
            OverallSystemStatus.ABSOLUTE_POSITION_KNOWN
        return loader_homed and elevator_homed

    @property
    def last_error(self) -> Union[DeviceError, int]:
        """The latched last error code"""
        try:
            return DeviceError(self._main_status.last_error)
        except IndexError:
            return self._main_status.last_error

    @property
    def _loader_type(self) -> LoaderType:
        return LoaderType.BETA if self.version else LoaderType.ALPHA

    def slot_state(self, slot_number: int) -> PayloadState:
        """Get the state of the given slot number: Present, Absent, or Unknown."""
        state: bool = self._main_status.slot_state & (1 << slot_number-1) > 0
        known: bool = self._main_status.slot_known & (1 << slot_number-1) > 0
        if known:
            if state:
                return PayloadState.PRESENT
            else:
                return PayloadState.ABSENT

        return PayloadState.UNKNOWN

    def get_version(self) -> tuple[int, int, int]:
        """ Get basic info from the device
        returns:
            version: Main version number  
            sub_version: Sub version number
            number_of_slots: Number of slots currently configured in the loader"""

        response: bytearray = self._connection.command(LoaderCommand.GET_VERSION)
        version = int.from_bytes(
            response[RESPONSE_BODY_OFFSET:RESPONSE_BODY_OFFSET+2],
            "little",
        )
        sub_version = int.from_bytes(
            response[RESPONSE_BODY_OFFSET+2:RESPONSE_BODY_OFFSET+4],
            "little",
        )
        number_of_slots = int.from_bytes(
            response[RESPONSE_BODY_OFFSET+4:RESPONSE_BODY_OFFSET+8],
            "little",
        )

        return version, sub_version, number_of_slots

    def home(self, axis: Axis = Axis.ALL, vacuum_safe: bool = True):
        """Initialize all motion axes, locating them with respect to their limit
        switches if necessary. Both axes are also moved to the home positions."""
        self._connection.command(
            LoaderCommand.HOME,
            bytearray([axis, vacuum_safe]),
            HOME_TIMEOUT
        )
        self._get_status()

    def stop(self, signum = None, frame = None):    # pylint: disable=unused-argument
        """Immediately stops loader motion/action
        args:
            signum and frame so that this can be used
            as an OS signal handler
        """
        self._status_connection.command(LoaderCommand.STOP)

    def load(self, slot_number: int):
        """Take whatever actions are necessary to place the sample in the provided slot
        into the imaging location.  The actions can include retracting and placing a sample
        already held in the gripper, picking the desired sample from its shelf, and extending
        to the imaging location."""
        self._connection.command(
            LoaderCommand.LOAD,
            bytearray([slot_number]),
            LOAD_TIMEOUT
        )

    def load_cassette(self, vacuum_safe: bool = True):
        """Bring the system to a state where the user can remove and replace the sample cassette.
        The first time this command completes, the user will be able to open the load lock door,
        remove the existing cassette (if any) and install a new cassette.  They would then close
        and lock the door and then cause this command to be issued a second time.  When this command
        is executed a second time, the load lock is locked and the cassette is mapped and made ready
        for use."""
        self._connection.command(
            LoaderCommand.LOAD_CASSETTE,
            bytearray([vacuum_safe]),
            LOAD_TIMEOUT
        )
        self._get_status()

    def evac(self):
        """Retract from the imaging position to the evac position.  When in the evac position, this
        command will cause the loader to return/extend to the imaging position."""
        self._connection.command(
            LoaderCommand.EVAC,
            timeout=EVAC_TIMEOUT
        )

    def clear_last_error(self):
        """Reset the latched last error code"""
        self._connection.command(LoaderCommand.CLEAR_LAST_ERROR)

    def clear(self):
        """Indicate to the loader that the gripper and cassette are both empty.
        Normally, the state of the gripper and the cassette would be found
        automatically by the loader during the LoadCassette process if the map
        sensor is in use.  This function is provided for convenience only
        and should ideally be used only in simulation mode."""
        self._connection.command(
            LoaderCommand.SET_SLOT_STATE,
            bytearray([255,255,255,255,0,0,0,0]),
        )
        self._get_status()

    def _get_status(self):
        resp: bytearray = self._status_connection.command(LoaderCommand.GET_STATUS)
        next_idx = RESPONSE_BODY_OFFSET

        next_idx = self._elevator_status.unpack(resp, next_idx, self._loader_type)
        next_idx = self._loader_status.unpack(resp, next_idx, self._loader_type)
        next_idx = self._main_status.unpack(resp, next_idx)
