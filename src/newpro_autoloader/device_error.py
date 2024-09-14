""" All AutoLoader error codes
Error codes that originate from the embedded controller have values less than 100"""

from enum import IntEnum

class DeviceError(IntEnum):
    # Everything's great
    NoError = 0,
    
    # Move types should be relative or absolute only
    InvalidMoveType = 1,
    
    # Axis is loader or elevator only
    InvalidAxis = 2,
    
    # Action requested incompatible with load lock being open (unused)
    LoadLockDoorOpen = 3,
    
    # Load lock was commanded to lock but already was locked (unused)
    AlreadyLocked = 4,
    
    # Load lock was commanded to unlock but already was unlocked (unused)
    AlreadyUnlocked = 5,
    
    # Internal communication between loader and motor drive failed
    CommFailure = 6,
    
    # Incorrect message start received from the motor drive
    InvalidStartByte = 7,
    
    # Incorrect message address received from the motor drive
    InvalidAddress = 8,
    
    # Incorrect sequence number received from the motor drive
    InvalidSequenceNumber = 9,
    
    # Invalid message checksum received from the motor drive
    InvalidCRC = 10,
    
    # Single axis move did not successfully complete within 35 seconds
    MoveTimeout = 11,
    
    # Motor phase angle offset detection did not complete successfully
    PhaseDetectFailed = 12,
    
    # Motor homing failed (unused)
    HomeFailed = 13,
    
    # Motor drive error: invalid request for an unknown parameter type
    InvalidDataParameter = 14,
    
    # Motor drive error.
    InvalidOpCode = 15,
    
    # Motor drive error.
    InvalidOpCodeForDynamicMotion = 16,
    
    # Motor drive error.
    InvalidReferenceFrame = 17,
    
    # Motor drive error.
    InvalidBridgeState = 18,
    
    # Motor drive error.
    UserDefinedFault = 19,
    
    # Deviation between commanded and actual motor position was too large
    PosFollowingError = 20,
    
    # Home move was too short
    HomeMoveFailed = 21,
    
    # Position capture was started but it was already running
    PositionCaptureAlreadyActive = 22,
    
    # Position capture was stopped but it wasn't running
    PositionCaptureAlreadyInactive = 23,
    
    # Mapping was started but it was already running
    MappingAlreadyActive = 24,
    
    # Mapping was stopped but it wasn't running
    MappingAlreadyInactive = 25,
    
    # The mapper amplifier alarm pin was activated
    MapSensorAlarm = 26,
    
    # Commanded motion could cause a collision
    UnsafeMove = 27,
    
    # Motion commanded but the axis is not homed
    NotHomed = 28,
    
    # Command recieved to advance to the next step but there are no pending steps
    NoActionPending = 29,
    
    # Grip was commanded =  but it's already gripping
    AlreadyGripping = 30,
    
    # UnGrip was commanded =  but it's not gripping
    NotGripping = 31,
    
    # Invalid slot requested in command: greater than the number of slots or less than 1
    InvalidSlotNumber = 32,
    
    # Command to pick from an empty slot
    EmptySlot = 33,
    
    # Command to place to a full slot
    FullSlot = 34,
    
    # Command received when there are still steps pending from a previous command
    StepsPending = 35,
    
    # Command to extend but loader axis is already extended
    AlreadyExtended = 36,
    
    # During homing =  extending =  or cassette load =  a move to a hard stop completed without a position following error
    NoHardStopFound = 37,
    
    # Command to unseal or unlock when the system is not in a safe state to do so
    UnsafeVacuum = 38,
    
    # Commanded position was outside of the allowed range for the axis
    OverPositionRangeLimit = 39,
    
    # Move was commanded to stop (simulation only)
    MoveStopped = 40,
    
    # Command received is invalid because a load cassette is in progress
    LoadCassetteInProgress = 41,
    
    # No mapper transitions were detected during a gripper inspection
    NoBeamBreakDetected = 42,
    
    # More mapper transitions than expected were detected during a gripper inspection
    ExtraBeamBreakDetected = 43,
    
    # Locations of mapper transitions during a gripper inspection were outside of the expected ranges
    BeamInspectInvalid = 44,
    
    # Motor drive failed to enable at the start of a move for an unknown reason
    MotionEngineEnableFailed = 45,
    
    # Move completed successfully but it was not within 50 um of the intended target position
    MoveFailed = 46,
    
    # Command to check gripper state but the beam inspect feature is not enabled
    BeamInspectDisabled = 47,
    
    # Gripper inspection result is not consistent with expected grip state
    UnexpectedGripperState = 48,
    
    # Gripper state is unknown =  cannot pick or place
    UnknownGripperState = 49,
    
    # Command received with stepping mode requested =  but command type doesn't support stepping
    SteppingUnsupported = 50,
    
    # Slot state is unknown =  cannot pick or place to that slot
    UnknownSlotState = 51,
    
    # Request to return payload to a slot must indicate the slot number from which the payload originated
    WrongSlot = 52,
    
    # Evac command can only happen if the loader axis is at either the extended or evac positions
    InvalidEvacStartPosition = 53,
    
    # More than 10 seconds have elapsed since the loader received a GetStatus command from the client
    HeartbeatTimeout = 54,
    
    # Motor controller indicates that the motor is stuck
    MotorStall = 55,
    
    # Any embedded error not in the above list
    Unknown = 56,

    
    # Unused
    SomethingIsUninitialized = 100,
    
    # Command code index received from the loader is not as expected
    InvalidResponseDataType = 101,
    
    # Message length received from the loader is too short
    InvalidResponseLength = 102,
    
    # Unused
    MemoryAllocationFailure = 103,
    
    # Unused
    ThreadFailure = 104,
    
    # Unused
    UnknownFailure = 105,
    
    # Unused
    InvalidArgumentValue = 106,
    
    # A function was called in the host that hasn't been implemented yet
    NotImplemented = 107,
    
    # Unused
    InvalidLogAddress = 108,
    
    # Unused
    DriverLoadFailure = 109,
    
    # Unused
    FileReadFailure = 110,
    
    # Unused
    DeviceErrorField = 111,
    
    # Message from loader doesn't have the correct start symbols =  length =  or checksum
    MalformedMessage = 112,
    
    # An attempt to open a connection to the loader failed
    ConnectionFailed = 113,
    
    # An attempt to read a message from the loader resulted in an exception throw or the full length of the message never came through
    NetworkReadFailed = 114,
    
    # An attempt to write a message to the loader resulted in an exception throw
    NetworkWriteFailed = 115,
    
    # Command to stop the map or retrieve the map data returned no data
    EmptyMapData = 116,
    
    # No response arrived from a command =  timeout length depends on command type
    Timeout = 117,


class DeviceException(Exception):
    def __init__(self, code: DeviceError):
        self._code = code

    @property
    def error_code(self) -> DeviceError:
        return self._code