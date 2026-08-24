import pytest, csv
from jv.core.engine import compute, angular_diff

# In CI, this loads the real committed CSV. Locally, it skips if missing.
try:
    with open('tests/independent_validation.csv', 'r') as f:
        VALIDATION_DATA = list(csv.DictReader(f))
except FileNotFoundError:
    VALIDATION_DATA = []

@pytest.mark.skipif(not VALIDATION_DATA, reason="No independent CSV present locally")
@pytest.mark.parametrize("row", VALIDATION_DATA)
def test_independent_validation_full_suite(row):
    y, m, d, h, mi = map(int, [row['y'], row['m'], row['d'], row['h'], row['mi']])
    result = compute(y, m, d, h, mi, row['tz'], float(row['lat']), float(row['lon']), 
                     ayan=row['ayan'], node=row['node'])
    tol = float(row.get('tolerance', 0.0001))
    for pid in ['su', 'mo', 'ma', 'me', 'jp', 've', 'sa', 'ra', 'ke']:
        expected_lon = float(row[f'{pid}_lon'])
        assert angular_diff(result['planets'][pid]['lon'], expected_lon) < tol
        assert result['planets'][pid]['sign'] == int(expected_lon // 30)
        expected_nak = int(expected_lon // (360/27))
        expected_pada = int((expected_lon % (360/27)) // (360/108)) + 1
        assert result['planets'][pid]['nak'] == expected_nak
        assert result['planets'][pid]['pada'] == expected_pada
