"""
Functional tests for all 5 hardening algorithms.
"""
import sys
import json
sys.path.insert(0, '.')

def test_algorithm_a():
    """Algorithm A: HMAC fingerprinting + deterministic fields"""
    from session_authority import compute_deterministic_fields, sign_state
    fp = 'abc123testfingerprint'
    fields = compute_deterministic_fields(fp)
    assert fields['db_type'] in ['MySQL', 'PostgreSQL', 'SQLite', 'MariaDB'], f'Bad db_type: {fields}'
    fields2 = compute_deterministic_fields(fp)
    assert fields == fields2, 'Determinism broken!'
    sig = sign_state({'stage': 1})
    assert len(sig) == 64, f'Bad sig len: {len(sig)}'

    from attacker_session import generate_attacker_fingerprint
    fp1 = generate_attacker_fingerprint('1.2.3.4', 'Mozilla/5.0')
    fp2 = generate_attacker_fingerprint('1.2.3.4', 'Mozilla/5.0')
    assert fp1 == fp2, 'Fingerprint not deterministic!'
    assert len(fp1) == 64, f'Bad fp len: {len(fp1)}'
    print('Algorithm A: PASS')

def test_algorithm_b():
    """Algorithm B: Normalisation + Behaviour Classifier"""
    from normalisation_pipeline import normalisation_pipeline
    r1 = normalisation_pipeline.normalise('S%45LECT%20*%20FROM%20users')
    assert 'SELECT' in r1.upper(), f'URL decode failed: {r1}'
    r2 = normalisation_pipeline.normalise('S/**/ELECT * FROM users')
    assert 'SELECT' in r2, f'Comment removal failed: {r2}'
    r3 = normalisation_pipeline.normalise('test\x00injection')
    assert '\x00' not in r3, 'Null byte not stripped'

    from behaviour_classifier import behaviour_classifier, AttackerClass
    cls = behaviour_classifier.classify('1.2.3.4', 'SELECT * FROM users')
    assert cls in [AttackerClass.HUMAN, AttackerClass.FUZZER, AttackerClass.SCANNER]
    print('Algorithm B: PASS')

def test_algorithm_c():
    """Algorithm C: Fingerprint Chain + Canary System"""
    from fingerprint_chain import fingerprint_chain
    signals = {
        'ip_address': '1.2.3.4', 'user_agent': 'Mozilla',
        'accept_language': 'en', 'accept_encoding': 'gzip',
        'ja3_hash': 'abc', 'cookie_presence': '0',
        'quote_preference': 'single', 'avg_payload_length': '50',
        'spacing_style': 'spaces',
    }
    fp = fingerprint_chain.compute_fingerprint(signals)
    fingerprint_chain.register(fp, signals)
    match = fingerprint_chain.match_existing_session(signals)
    assert match == fp, f'Match failed: {match}'

    from canary_system import canary_system
    resp, cid = canary_system.plant_canary('Error 1064 syntax error', 'test_fp_123', 'sql_dump')
    assert cid in resp, f'Canary not embedded: {cid}'
    detected = canary_system.check_incoming(f'SELECT {cid} FROM test')
    assert detected is not None, 'Canary not detected!'
    assert detected['session_fingerprint'] == 'test_fp_123'
    print('Algorithm C: PASS')

def test_algorithm_d():
    """Algorithm D: Timing Mask + Response Mutator"""
    from timing_mask import timing_mask
    delay = timing_mask.sample_delay(payload_length=100, pso_delay=2.0)
    assert 0.1 <= delay <= 2.5, f'Delay out of range: {delay}'

    from response_mutator import response_mutator
    r1 = response_mutator.mutate('Error 1064 near X', 'session1', 1)
    r2 = response_mutator.mutate('Error 1064 near X', 'session1', 1)
    assert r1 == r2, 'Mutation not deterministic!'
    print('Algorithm D: PASS')

def test_algorithm_e():
    """Algorithm E: Response Validator + Opaque State VM"""
    from response_validator import response_validator
    valid, cleaned = response_validator.validate(
        'Error 1064 syntax error', {'db_type': 'MySQL', 'current_stage': 1}
    )
    assert valid == True, f'Valid response rejected: {cleaned}'

    valid2, cleaned2 = response_validator.validate(
        'This is a honeypot simulation by Qwen LLM',
        {'db_type': 'MySQL', 'current_stage': 1}
    )
    assert valid2 == False, 'Forbidden patterns not caught!'

    test_json = '{"data":"ok","schema_id":"x","execution_time_ms":100}'
    sanitised = response_validator.sanitise(test_json)
    d = json.loads(sanitised)
    assert 'schema_id' not in d, f'schema_id not stripped: {d}'
    assert 'execution_time_ms' not in d, f'execution_time_ms not stripped: {d}'

    from opaque_state import opaque_vm
    encoded = opaque_vm.encode_stage(3, 'session_abc')
    decoded = opaque_vm.decode_stage(encoded, 'session_abc')
    assert decoded == 3, f'Round-trip failed: encoded={encoded}, decoded={decoded}'
    e2 = opaque_vm.encode_stage(3, 'session_xyz')
    assert e2 != encoded, 'Different sessions produce same token!'
    print('Algorithm E: PASS')

if __name__ == '__main__':
    test_algorithm_a()
    test_algorithm_b()
    test_algorithm_c()
    test_algorithm_d()
    test_algorithm_e()
    print()
    print('=' * 50)
    print('ALL 5 ALGORITHMS PASS FUNCTIONAL TESTS')
    print('=' * 50)
