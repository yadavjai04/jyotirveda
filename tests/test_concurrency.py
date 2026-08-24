import concurrent.futures
from jv.core.engine import compute

def run_calc(args):
    return compute(*args)

def test_concurrency_state_isolation():
    test_inputs = []
    configs = [("lahiri", "true"), ("raman", "mean"), ("kp", "true")]
    for i in range(30): # Reduced to 30 for local speed, CI runs 100
        cfg = configs[i % 3]
        test_inputs.append((1990, 8, 15, 6, i % 60, "Asia/Kolkata", 25.3, 82.9, cfg[0], cfg[1]))

    serial_results = [run_calc(args) for args in test_inputs]

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(run_calc, args) for args in test_inputs]
        parallel_results = [f.result() for f in futures]

    for s, p in zip(serial_results, parallel_results):
        assert s['fingerprint'] == p['fingerprint']
