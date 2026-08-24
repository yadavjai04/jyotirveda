from jv.core.engine import compute

def test_fingerprint_determinism():
    kwargs = dict(tz_name="Asia/Kolkata", lat=25.3176, lon=82.9739, ayan="lahiri", node="true")
    a = compute(1990, 8, 15, 6, 24, **kwargs)
    b = compute(1990, 8, 15, 6, 24, **kwargs)
    assert a["fingerprint"] == b["fingerprint"]

def test_fingerprint_sensitivity():
    base = compute(1990, 8, 15, 6, 0, "Asia/Kolkata", 25.3, 82.9, ayan="lahiri", node="true")
    assert base['fingerprint'] != compute(1990, 8, 15, 6, 0, "UTC", 25.3, 82.9, ayan="lahiri", node="true")['fingerprint']
    assert base['fingerprint'] != compute(1990, 8, 15, 6, 0, "Asia/Kolkata", 25.3, 82.9, ayan="raman", node="true")['fingerprint']
    assert base['fingerprint'] != compute(1990, 8, 15, 6, 0, "Asia/Kolkata", 25.3, 82.9, ayan="lahiri", node="mean")['fingerprint']
