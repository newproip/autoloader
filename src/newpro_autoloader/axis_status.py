"""Functions for parsing autoloader status at the per-axis level"""
from enum import IntEnum
from struct import unpack_from
from typing import Optional

SIZE_OF_ACTION_NAME = 32

class OverallSystemStatus(IntEnum):
    """System status bitfield"""
    ABSOLUTE_POSITION_KNOWN = 1
    PHASE_DETECTED = 2
    SERVO_ENABLED = 4
    IN_MOTION = 8

class LoaderType(IntEnum):
    """Autoloader compatability version"""
    ALPHA = 0
    BETA = 1

class MainStatus:
    """Status object related to the autoloader overall"""

    def __init__(self):
        self._slot_known: int = 0
        self._slot_state: int = 0
        self._closest_slot: int = 0
        self._percent_extended: float = 0
        self._current_action: str = ""
        self._last_error: int = 0
        self._gripped_from_slot: int = 0

    def unpack(self, data: bytearray, start_idx: int) -> int:
        """Initialize fields based on the incoming byte stream status"""
        self._slot_known, = unpack_from("I", data, start_idx)
        start_idx += 4

        self._slot_state, = unpack_from("I", data, start_idx)
        start_idx += 4

        self._closest_slot, = unpack_from("i", data, start_idx)
        start_idx += 4

        self._percent_extended, = unpack_from("d", data, start_idx)
        start_idx += 8

        self._current_action, = unpack_from(f"{SIZE_OF_ACTION_NAME}s", data, start_idx)
        start_idx += SIZE_OF_ACTION_NAME

        self._last_error, = unpack_from("I", data, start_idx)
        start_idx += 4

        self._gripped_from_slot, = unpack_from("i", data, start_idx)
        start_idx += 4

        return start_idx

    @property
    def gripped_from_slot(self):
        """A non-zero value indicates the shelf from which the currently
        gripper payload came from"""
        return self._gripped_from_slot

    @property
    def last_error(self):
        """The last error code raised during operaton"""
        return self._last_error

    @property
    def slot_state(self):
        """Bitfield indicating the payload state of all slots"""
        return self._slot_state

    @property
    def slot_known(self):
        """Bitfield indicating the payload KNOWN state of all slots"""
        return self._slot_known

class AxisStatus:
    """Status object related to one or the other autoloader axes (elevator or loader)"""

    def __init__(self):
        self._position: float = 0.0
        self._overall_status: Optional[OverallSystemStatus] = None

        self._overall_status: int = 0
        self._drive_status: int = 0
        self._step_count_status: int = 0
        self._actual_current_status: int = 0
        self._motion_status: int = 0
        self._motor_position: int = 0
        self._encoder_position: int = 0
        self._motor_velocity: int = 0
        self._pwm_status: int = 0
        self._general_status: int = 0

    def unpack(self, data: bytearray, start_idx: int, loader_type: LoaderType) -> int:
        """Initialize fields based on the incoming byte stream status"""
        self._position, = unpack_from("d", data, start_idx)
        start_idx += 8

        if loader_type == LoaderType.BETA:
            self._overall_status, = unpack_from("H", data, start_idx)
            start_idx += 2

            self._drive_status, = unpack_from("I", data, start_idx)
            start_idx += 4

            self._step_count_status, = unpack_from("I", data, start_idx)
            start_idx += 4

            self._actual_current_status, = unpack_from("I", data, start_idx)
            start_idx += 4

            self._motion_status, = unpack_from("I", data, start_idx)
            start_idx += 4

            self._motor_position, = unpack_from("I", data, start_idx)
            start_idx += 4

            self._encoder_position, = unpack_from("I", data, start_idx)
            start_idx += 4

            self._motor_velocity, = unpack_from("I", data, start_idx)
            start_idx += 4

            self._pwm_status, = unpack_from("I", data, start_idx)
            start_idx += 4

            self._general_status, = unpack_from("I", data, start_idx)
            start_idx += 4
        else:
            # ElectricalCyclePosition
            start_idx += 4
            # LatchedEncoderPosition
            start_idx += 4
            # PhaseSyncError
            start_idx += 4
            # StatorAngle
            start_idx += 2
            # RotorAngle
            start_idx += 2
            # StatorFrequency
            start_idx += 2
            # RotorFrequency
            start_idx += 2
            # CommutationCounts
            start_idx += 4
            # CapturedElectricalCyclePosition
            start_idx += 4
            # PhaseSyncAdjustment
            start_idx += 4
            # StepCyclePosition
            start_idx += 4
            # PositionCapture
            start_idx += 4

            self._overall_status, = unpack_from("H", data, start_idx)
            start_idx += 2

            start_idx += 50

        return start_idx

    @property
    def status(self):
        """Axis status"""
        return self._overall_status
