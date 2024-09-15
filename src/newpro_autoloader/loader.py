from enum import IntEnum
from threading import Thread
from time import sleep

from newpro_autoloader.axis_status import AxisStatus
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
        """Create a loader interface.  Does not try to connect until
        a command is executed."""

        self._addresses = [address, fallback_address]
        self._connection: LoaderConnection = LoaderConnection(self._addresses, PORT_NUMBER)
        self._status_connection: LoaderConnection = LoaderConnection(self._addresses, PORT_NUMBER_STATUS)
        self._update_thread = Thread(target=self._updater, name="Update thread", daemon=True)
        self._run_thread = False

    def __enter__(self):
        self._run_thread = True
        self._update_thread.start()
        return self
    
    def __exit__(self, *args):
        self._run_thread = False

    # is_gripped
    # index_loaded
    # is_homed
    # is_cassette_loading
    # last_error
    # slot states

    def _get_status(self):
        resp: bytearray = self._status_connection.command(LoaderCommand.GET_STATUS)
        next_idx = RESPONSE_BODY_OFFSET

        self._elevator_status: AxisStatus = AxisStatus()
        next_idx = self._elevator_status.unpack(resp, next_idx)

        self._loader_status: AxisStatus = AxisStatus()
        next_idx = self._loader_status.unpack(resp, next_idx)

    def get_version(self) -> tuple[int, int, int]:
        """ Get basic info from the device
        returns:
            version: Main version number  
            subVersion: Sub version number
            numberOfSlots: Number of slots currently configured in the loader"""

        response: bytearray = self._connection.command(LoaderCommand.GET_VERSION)
        version = int.from_bytes(response[RESPONSE_BODY_OFFSET:RESPONSE_BODY_OFFSET+1], "little")
        sub_version = int.from_bytes(response[RESPONSE_BODY_OFFSET+2:RESPONSE_BODY_OFFSET+3], "little")
        number_of_slots = int.from_bytes(response[RESPONSE_BODY_OFFSET+4:RESPONSE_BODY_OFFSET+7], "little")

        return version, sub_version, number_of_slots
    
    def home(self, axis: Axis = Axis.All, vacuum_safe: bool = True):
        self._connection.command(
            LoaderCommand.HOME,
            bytearray([axis, vacuum_safe]),
            HOME_TIMEOUT
        )
        
    def stop(self):
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

    def evac(self):
        self._connection.command(
            LoaderCommand.EVAC,
            timeout=EVAC_TIMEOUT
        )

    def clear_last_error(self):
        self._connection.command(LoaderCommand.CLEAR_LAST_ERROR)
