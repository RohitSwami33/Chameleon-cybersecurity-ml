#!/usr/bin/env python3
"""
Quick test for refactored modules - minimal dependencies
Tests core logic without external API calls
"""

import sys
import os
import hashlib
import json
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Backend'))

print("=" * 70)
print(" CHAMELEON MODULE VERIFICATION")
print("=" * 70)

all_passed = True

# Test 1: Merkle Tree Integrity (no external deps)
print("\n[1] Testing Merkle Tree Integrity...")
try:
    from integrity import hash_log_entry, MerkleTree, MerkleLogger
    
    test_log = {
        "id": "test-123",
        "timestamp": "2024-01-15T10:30:00Z",
        "attacker_ip": "192.168.1.100",
        "command_entered": "ls -la",
        "response_sent": "total 48"
    }
    
    log_hash = hash_log_entry(test_log)
    assert len(log_hash) == 64, f"Hash should be 64 chars, got {len(log_hash)}"
    print(f"   ✅ hash_log_entry works: {log_hash[:16]}...")
    
    logs = [
        {"id": "1", "command_entered": "cmd1"},
        {"id": "2", "command_entered": "cmd2"},
        {"id": "3", "command_entered": "cmd3"},
    ]
    
    tree = MerkleTree(logs)
    assert tree.root_hash is not None, "Tree should have root hash"
    print(f"   ✅ MerkleTree with {len(logs)} logs: {tree.root_hash[:16]}...")
    
    proof = tree.get_proof(0)
    assert len(proof) > 0, "Should have proof"
    print(f"   ✅ Merkle proof: {len(proof)} steps")
    
    is_valid = MerkleTree.verify_proof(tree.leaf_hashes[0], proof, tree.root_hash)
    assert is_valid, "Proof should be valid"
    print("   ✅ Proof verification works")
    
    logger = MerkleLogger()
    logger.add_logs(logs)
    root = logger.build_tree()
    assert root is not None, "Logger should build tree"
    print(f"   ✅ MerkleLogger works: {root[:16]}...")
    
    print("   ✅ Merkle Tree Integrity: ALL TESTS PASSED")
    
except Exception as e:
    print(f"   ❌ Merkle Tree test failed: {e}")
    all_passed = False
    import traceback
    traceback.print_exc()

# Test 2: Edge Cases
print("\n[2] Testing Edge Cases...")
try:
    from integrity import MerkleTree, MerkleLogger, hash_log_entry
    
    empty_tree = MerkleTree([])
    assert empty_tree.root_hash is None, "Empty tree should have None root"
    print("   ✅ Empty tree returns None")
    
    single_tree = MerkleTree([{"id": "1"}])
    assert single_tree.root_hash is not None, "Single element should have root"
    print("   ✅ Single element tree works")
    
    odd_tree = MerkleTree([{"id": "1"}, {"id": "2"}, {"id": "3"}])
    assert odd_tree.root_hash is not None, "Odd elements should have root"
    print("   ✅ Odd number of elements works")
    
    log_with_none = {"id": "test", "value": None, "other": "data"}
    hash_result = hash_log_entry(log_with_none)
    assert hash_result is not None, "Should hash logs with None values"
    print("   ✅ None value handling works")
    
    print("   ✅ Edge Cases: ALL TESTS PASSED")
    
except Exception as e:
    print(f"   ❌ Edge cases failed: {e}")
    all_passed = False
    import traceback
    traceback.print_exc()

# Test 3: Mock SQLAlchemy Object Handling
print("\n[3] Testing SQLAlchemy Object Handling...")
try:
    from integrity import MerkleLogger
    
    class MockHoneypotLog:
        def __init__(self, id, cmd):
            self.id = id
            self.timestamp = datetime.utcnow()
            self.attacker_ip = "1.2.3.4"
            self.command_entered = cmd
            self.response_sent = f"response for {cmd}"
            self.metadata = {"test": True}
        
        def to_dict(self):
            return {
                "id": str(self.id),
                "timestamp": self.timestamp.isoformat(),
                "attacker_ip": self.attacker_ip,
                "command_entered": self.command_entered,
                "response_sent": self.response_sent,
                "metadata": self.metadata
            }
    
    mock_logs = [MockHoneypotLog(i, f"command{i}") for i in range(5)]
    
    logger = MerkleLogger()
    hashes = logger.add_logs(mock_logs)
    assert len(hashes) == 5, f"Should have 5 hashes, got {len(hashes)}"
    print(f"   ✅ add_logs() handles SQLAlchemy-like objects")
    
    root = logger.build_tree()
    assert root is not None, "Should build tree from objects"
    print(f"   ✅ build_tree() from objects: {root[:16]}...")
    
    stats = logger.get_stats()
    assert stats["log_count"] == 5, f"Should have 5 logs, got {stats['log_count']}"
    print(f"   ✅ Stats correct: {stats['log_count']} logs")
    
    print("   ✅ SQLAlchemy Object Handling: ALL TESTS PASSED")
    
except Exception as e:
    print(f"   ❌ SQLAlchemy object handling failed: {e}")
    all_passed = False
    import traceback
    traceback.print_exc()

# Test 4: LLM Controller Static Fallback
print("\n[4] Testing LLM Controller Static Fallback...")
try:
    from llm_controller import LLMController
    
    controller = LLMController(provider="deepseek")
    
    response = controller._static_fallback("whoami")
    assert response == "www-data", f"Expected 'www-data', got '{response}'"
    print("   ✅ whoami -> 'www-data'")
    
    response = controller._static_fallback("id")
    assert "uid=33" in response, f"Expected uid info, got '{response}'"
    print("   ✅ id -> uid info")
    
    response = controller._static_fallback("pwd")
    assert response == "/var/www/html", f"Expected '/var/www/html', got '{response}'"
    print("   ✅ pwd -> '/var/www/html'")
    
    response = controller._static_fallback("sudo su")
    assert "sudoers" in response, f"Expected sudoers error, got '{response}'"
    print("   ✅ sudo -> permission denied")
    
    response = controller._static_fallback("rm -rf /")
    assert "dangerous" in response.lower() or "preserve-root" in response.lower(), f"Expected dangerous warning, got '{response}'"
    print("   ✅ rm -rf / -> warning")
    
    response = controller._static_fallback("unknown_command_xyz")
    assert "command not found" in response, f"Expected command not found, got '{response}'"
    print("   ✅ unknown command -> not found")
    
    print("   ✅ LLM Static Fallback: ALL TESTS PASSED")
    
except Exception as e:
    print(f"   ❌ LLM Controller test failed: {e}")
    all_passed = False
    import traceback
    traceback.print_exc()

# Test 5: Command History
print("\n[5] Testing Command History...")
try:
    from llm_controller import CommandHistory
    
    history = CommandHistory()
    history.add_command("ls -la", "total 48\n...")
    history.add_command("whoami", "www-data")
    history.add_command("pwd", "/var/www/html")
    
    assert len(history.commands) == 3, f"Should have 3 commands, got {len(history.commands)}"
    print("   ✅ Commands added to history")
    
    context = history.get_context(last_n=2)
    assert "whoami" in context, "Context should contain whoami"
    assert "pwd" in context, "Context should contain pwd"
    print("   ✅ get_context() works")
    
    history_dict = history.to_dict()
    assert len(history_dict) == 3, "Dict should have 3 entries"
    print("   ✅ to_dict() works")
    
    for i in range(25):
        history.add_command(f"cmd{i}", f"response{i}")
    assert len(history.commands) == 20, f"Should cap at 20, got {len(history.commands)}"
    print("   ✅ History capped at max_history")
    
    print("   ✅ Command History: ALL TESTS PASSED")
    
except Exception as e:
    print(f"   ❌ Command history test failed: {e}")
    all_passed = False
    import traceback
    traceback.print_exc()

# Test 6: Configuration Settings
print("\n[6] Testing Configuration...")
try:
    from config import settings
    
    assert hasattr(settings, 'DATABASE_URL'), "Missing DATABASE_URL"
    print(f"   ✅ DATABASE_URL exists")
    
    assert hasattr(settings, 'SYNC_DATABASE_URL'), "Missing SYNC_DATABASE_URL"
    print(f"   ✅ SYNC_DATABASE_URL exists")
    
    assert hasattr(settings, 'DEEPSEEK_API_KEY'), "Missing DEEPSEEK_API_KEY"
    print(f"   ✅ DEEPSEEK_API_KEY exists")
    
    assert hasattr(settings, 'LLM_PROVIDER'), "Missing LLM_PROVIDER"
    print(f"   ✅ LLM_PROVIDER: {settings.LLM_PROVIDER}")
    
    assert hasattr(settings, 'USE_LLM_DECEPTION'), "Missing USE_LLM_DECEPTION"
    print(f"   ✅ USE_LLM_DECEPTION: {settings.USE_LLM_DECEPTION}")
    
    print("   ✅ Configuration: ALL TESTS PASSED")
    
except Exception as e:
    print(f"   ❌ Configuration test failed: {e}")
    all_passed = False
    import traceback
    traceback.print_exc()

# Summary
print("\n" + "=" * 70)
if all_passed:
    print(" ✅ ALL TESTS PASSED!")
    print("=" * 70)
    sys.exit(0)
else:
    print(" ⚠️  SOME TESTS FAILED")
    print("=" * 70)
    sys.exit(1)
