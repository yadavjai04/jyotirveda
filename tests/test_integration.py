from jv.core.engine import compute

def test_full_chart_integration():
    res = compute(1990, 8, 15, 6, 24, "Asia/Kolkata", 25.3176, 82.9739)
    lagna_sign = res['lagna_sign']
    for pid, p_data in res['planets'].items():
        expected_house = ((p_data['sign'] - lagna_sign) % 12) + 1
        assert res['houses'][pid] == expected_house
