"""Test threshold logic."""
from fake_sensors.threshold_logic import is_outside_threshold
import pytest


@pytest.mark.parametrize('value, threshold, expected', [
    (499, 500, False),
    (500, 500, False),
    (501, 500, True),
])
def test_is_outside_threshold(value, threshold, expected):
    """Test case."""
    assert is_outside_threshold(value, threshold) == expected
