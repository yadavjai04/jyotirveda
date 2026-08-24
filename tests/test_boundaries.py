from jv.core.engine import angular_diff

def test_angular_diff_circular():
    assert angular_diff(359.9, 0.1) == 0.2
    assert angular_diff(0.1, 359.9) == 0.2
    assert angular_diff(180.0, 0.0) == 180.0
    assert angular_diff(45.0, 45.0) == 0.0
