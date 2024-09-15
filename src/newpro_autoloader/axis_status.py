from enum import IntEnum
from struct import unpack_from

SIZE_OF_ACTION_NAME = 32

class OverallSystemStatus(IntEnum):
    AbsolutePositionKnown = 1,
    PhaseDetected = 2,
    ServoEnbled = 4,
    InMotion = 8,

class MainStatus:

    def unpack(self, data: bytearray, start_idx: int) -> int:
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

class AxisStatus:

    def __init__(self):
        self._position: float = 0.0

    def unpack(self, data: bytearray, start_idx: int) -> int:
        self._position, = unpack_from("d", data, start_idx)
        start_idx += 8

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

        return start_idx