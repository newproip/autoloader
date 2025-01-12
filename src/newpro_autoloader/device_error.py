""" All AutoLoader error codes
Error codes that originate from the embedded controller have values less than 100"""

from enum import IntEnum

class DeviceError(IntEnum):
    """Autoloader error codes"""
    # Everything's great
    NO_ERROR = 0

    # Move types should be relative or absolute only
    INVALID_MOVE_TYPE = 1

    # Axis is loader or elevator only
    INVALID_AXIS = 2

    # Action requested incompatible with load lock being open (unused)
    LOAD_LOCK_DOOR_OPEN = 3

    # Load lock was commanded to lock but already was locked (unused)
    ALREADY_LOCKED = 4

    # Load lock was commanded to unlock but already was unlocked (unused)
    ALREADY_UNLOCKED = 5

    # Internal communication between loader and motor drive failed
    COMM_FAILURE = 6

    # Incorrect message start received from the motor drive
    INVALID_START_BYTE = 7

    # Incorrect message address received from the motor drive
    INVALID_ADDRESS = 8

    # Incorrect sequence number received from the motor drive
    INVALID_SEQUENCE_NUMBER = 9

    # Invalid message checksum received from the motor drive
    INVALID_CRC = 10

    # Single axis move did not successfully complete within 35 seconds
    MOVE_TIMEOUT = 11

    # Motor phase angle offset detection did not complete successfully
    PHASE_DETECT_FAILED = 12

    # Motor homing failed (unused)
    HOME_FAILED = 13

    # Motor drive error: invalid request for an unknown parameter type
    INVALID_DATA_PARAMETER = 14

    # Motor drive error.
    INVALID_OP_CODE = 15

    # Motor drive error.
    INVALID_OP_CODE_FOR_DYNAMIC_MOTION = 16

    # Motor drive error.
    INVALID_REFERENCE_FRAME = 17

    # Motor drive error.
    INVALID_BRIDGE_STATE = 18

    # Motor drive error.
    USER_DEFINED_FAULT = 19

    # Deviation between commanded and actual motor position was too large
    POS_FOLLOWING_ERROR = 20

    # Home move was too short
    HOME_MOVE_FAILED = 21

    # Position capture was started but it was already running
    POSITION_CAPTURE_ALREADY_ACTIVE = 22

    # Position capture was stopped but it wasn't running
    POSITION_CAPTURE_ALREADY_INACTIVE = 23

    # Mapping was started but it was already running
    MAPPING_ALREADY_ACTIVE = 24

    # Mapping was stopped but it wasn't running
    MAPPING_ALREADY_INACTIVE = 25

    # The mapper amplifier alarm pin was activated
    MAP_SENSOR_ALARM = 26

    # Commanded motion could cause a collision
    UNSAFE_MOVE = 27

    # Motion commanded but the axis is not homed
    NOT_HOMED = 28

    # Command recieved to advance to the next step but there are no pending steps
    NO_ACTION_PENDING = 29

    # Grip was commanded =  but it's already gripping
    ALREADY_GRIPPING = 30

    # UnGrip was commanded =  but it's not gripping
    NOT_GRIPPING = 31

    # Invalid slot requested in command: greater than the number of slots or less than 1
    INVALID_SLOT_NUMBER = 32

    # Command to pick from an empty slot
    EMPTY_SLOT = 33

    # Command to place to a full slot
    FULL_SLOT = 34

    # Command received when there are still steps pending from a previous command
    STEPS_PENDING = 35

    # Command to extend but loader axis is already extended
    ALREADY_EXTENDED = 36

    # During homing =  extending =  or cassette load =  a move to a hard stop
    # completed without a position following error
    NO_HARD_STOP_FOUND = 37

    # Command to unseal or unlock when the system is not in a safe state to do so
    UNSAFE_VACUUM = 38

    # Commanded position was outside of the allowed range for the axis
    OVER_POSITION_RANGE_LIMIT = 39

    # Move was commanded to stop (simulation only)
    MOVE_STOPPED = 40

    # Command received is invalid because a load cassette is in progress
    LOAD_CASSETTE_IN_PROGRESS = 41

    # No mapper transitions were detected during a gripper inspection
    NO_BEAM_BREAK_DETECTED = 42

    # More mapper transitions than expected were detected during a gripper inspection
    EXTRA_BEAM_BREAK_DETECTED = 43

    # Locations of mapper transitions during a gripper inspection were
    # outside of the expected ranges
    BEAM_INSPECT_INVALID = 44

    # Motor drive failed to enable at the start of a move for an unknown reason
    MOTION_ENGINE_ENABLE_FAILED = 45

    # Move completed successfully but it was not within 50 um of the intended target position
    MOVE_FAILED = 46

    # Command to check gripper state but the beam inspect feature is not enabled
    BEAM_INSPECT_DISABLED = 47

    # Gripper inspection result is not consistent with expected grip state
    UNEXPECTED_GRIPPER_STATE = 48

    # Gripper state is unknown =  cannot pick or place
    UNKNOWN_GRIPPER_STATE = 49

    # Command received with stepping mode requested =  but command type doesn't support stepping
    STEPPING_UNSUPPORTED = 50

    # Slot state is unknown =  cannot pick or place to that slot
    UNKNOWN_SLOT_STATE = 51

    # Request to return payload to a slot must indicate the slot number from which
    # the payload originated
    WRONG_SLOT = 52

    # Evac command can only happen if the loader axis is at either the extended or evac positions
    INVALID_EVAC_START_POSITION = 53

    # More than 10 seconds have elapsed since the loader received a GetStatus
    # command from the client
    HEARTBEAT_TIMEOUT = 54

    # Motor controller indicates that the motor is stuck
    MOTOR_STALL = 55

    # Any embedded error not in the above list
    UNKNOWN = 56


    # Unused
    SOMETHING_IS_UNINITIALIZED = 100

    # Command code index received from the loader is not as expected
    INVALID_RESPONSE_DATA_TYPE = 101

    # Message length received from the loader is too short
    INVALID_RESPONSE_LENGTH = 102

    # Unused
    MEMORY_ALLOCATION_FAILURE = 103

    # Unused
    THREAD_FAILURE = 104

    # Unused
    UNKNOWN_FAILURE = 105

    # Unused
    INVALID_ARGUMENT_VALUE = 106

    # A function was called in the host that hasn't been implemented yet
    NOT_IMPLEMENTED = 107

    # Unused
    INVALID_LOG_ADDRESS = 108

    # Unused
    DRIVER_LOAD_FAILURE = 109

    # Unused
    FILE_READ_FAILURE = 110

    # Unused
    DEVICE_ERROR_FIELD = 111

    # Message from loader doesn't have the correct start symbols =  length =  or checksum
    MALFORMED_MESSAGE = 112

    # An attempt to open a connection to the loader failed
    CONNECTION_FAILED = 113

    # An attempt to read a message from the loader resulted in an exception throw or the
    # full length of the message never came through
    NETWORK_READ_FAILED = 114

    # An attempt to write a message to the loader resulted in an exception throw
    NETWORK_WRITE_FAILED = 115

    # Command to stop the map or retrieve the map data returned no data
    EMPTY_MAP_DATA = 116

    # No response arrived from a command =  timeout length depends on command type
    TIMEOUT = 117

    # Action was cancelled
    CANCELLED = 118


class DeviceException(Exception):
    """Autoloader exception with error code"""
    def __init__(self, code: DeviceError):
        self._code = code

    def __str__(self) -> str:
        return self._code.name

    @property
    def error_code(self) -> DeviceError:
        """Autoloader error code thrown with exception"""
        return self._code
