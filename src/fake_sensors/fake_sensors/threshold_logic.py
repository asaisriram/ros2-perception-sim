"""Logic function for received message data."""


def is_outside_threshold(value: int, threshold: int) -> bool:
    """Check if received value is outside threshold."""
    return value > threshold
