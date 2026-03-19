# Test Results — Novel Equations Test Suite

## How to Run
```bash
cd /path/to/Chameleon-cybersecurity-ml/Backend

# Install dependencies
python3 -m pip install pytest pytest-asyncio --break-system-packages

# Run individual suites
python3 -m pytest tests/test_tc_pso_equations.py     -v --asyncio-mode=auto -s
python3 -m pytest tests/test_s_rrt_equations.py      -v --asyncio-mode=auto -s
python3 -m pytest tests/test_mathematical_proofs.py  -v --asyncio-mode=auto -s
python3 -m pytest tests/test_comparison_algorithms.py -v --asyncio-mode=auto -s

# Run full suite
python3 -m pytest tests/ -v --asyncio-mode=auto -s
```

## Test Summary

| Suite | Tests | Result |
|-------|-------|--------|
| `test_tc_pso_equations.py`      | 24 | ✅ 24/24 PASS |
| `test_s_rrt_equations.py`       | 27 | ✅ 27/27 PASS |
| `test_mathematical_proofs.py`   | 31 | ✅ 31/31 PASS |
| `test_comparison_algorithms.py` |  9 | ✅ 9/9   PASS |
| **Total**                       | **91** | **✅ 91/91 PASS** |

## Result Files

| File | Contents |
|------|----------|
| `tc_pso_and_proofs_results.txt` | Full Eq 1+2 and proofs output |
| `s_rrt_results.txt`             | Full Eq 3+4 output |
| `comparison_results.txt`        | Algorithm comparison output |
| `full_suite_results.txt`        | Complete 91-test run |
| `COMPARISON_REPORT.md`          | Research-quality comparison report |
