"""Logic function for received message data."""

from enum import StrEnum


RAMP_PERIOD = 60.0      # sawtooth wraps every 60 s

TEMP_BASE_C = 20.0        # base temperature
TEMP_RATE_C_PER_S = 0.5   # rise rate -> 20.0 .. 50.0 C over the period

PLAUSI_PARAM = 0.5  #threshold check parameter


class ErrorStatus(StrEnum):
    NO_ERROR = "NO_ERROR"
    DATA_INCONSISTENCY_ERROR = "DATA_INCONSISTENCY_ERROR"
    PLAUSI_ERROR = "PLAUSI_ERROR"
    THRESHOLD_ERROR = "THRESHOLD_ERROR"

current_state = ErrorStatus.NO_ERROR


def get_ground_truth_data(clock_data):
    """Return factored data rounded to 2 decimals"""
    return (clock_data / 1e9) % RAMP_PERIOD


def temperature_conversion(counter):
    """Check temperature conversion logic using counter data."""
    factor = TEMP_RATE_C_PER_S
    offset = TEMP_BASE_C
    return offset + (factor * counter)


def is_data_inconsistent(counter, temperature) -> bool:
    """Check data consistency."""
    if None in (counter, temperature):
        current_state =  ErrorStatus.DATA_INCONSISTENCY_ERROR
    return current_state


def check_sensor_plausibility(counter, temperature) -> bool:
    """Sensor plausibility check."""
    temperature_calc = temperature_conversion(counter)
    if abs(temperature - temperature_calc) > PLAUSI_PARAM:
        current_state =  ErrorStatus.PLAUSI_ERROR
    return current_state


def is_outside_threshold(counter, threshold) -> bool:
    """Check if received value is outside threshold."""
    if counter > threshold:
        current_state =  ErrorStatus.THRESHOLD_ERROR
    return current_state