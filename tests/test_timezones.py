import pytest
from jv.core.engine import compute

def test_dst_nonexistent_time():
    # US DST Spring Forward 2024-03-10 02:30 (Does not exist)
    with pytest.raises(ValueError, match="Nonexistent local time"):
        compute(2024, 3, 10, 2, 30, "America/New_York", 40.71, -74.00)

def test_dst_ambiguous_time():
    # US DST Fall Back 2024-11-03 01:30 (Happens twice)
    with pytest.raises(ValueError, match="Ambiguous local time"):
        compute(2024, 11, 3, 1, 30, "America/New_York", 40.71, -74.00)
