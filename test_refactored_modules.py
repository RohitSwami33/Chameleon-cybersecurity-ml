#!/usr/bin/env python3
"""
Comprehensive Test Suite for Refactored Chameleon Modules
==========================================================

Tests:
1. LLM Controller (DeepSeek API)
2. Merkle Tree Integrity
3. PostgreSQL Database Module
4. Edge Cases

Run with: python test_refactored_modules.py
"""

import sys
import os
import asyncio
import hashlib
import json
from datetime import datetime
from typing import Dict, Any, List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Backend'))

print("=" * 70)
print(" CHAMELEON REFACTORED MODULES TEST SUITE")
print("=" * 70)


class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def success(self, test_name: str):
        self.passed += 1
        print(f"   ✅ {test_name}")
    
    def failure(self, test_name: str, error: str):
        self.failed += 1
        self.errors.append((test_name, error))
        print(f"   ❌ {test_name}: {error}")
    
    def summary(self):
        print("\n" + "=" * 70)
        print(f" RESULTS: {self.passed} passed, {self.failed} failed")
        if self.errors:
            print("\nFailed tests:")
            for name, error in self.errors:
                print(f"  - {name}: {error}")
        print("=" * 70)
        return self.failed == 0


results = TestResult()


# ============================================================
# TEST 1: Configuration Module
# ============================================================
print("\n" + "=" * 70)
print(" TEST 1: Configuration Module")
print("=" * 70)

try:
    from config import settings
    
    if hasattr(settings, 'DEEPSEEK_API_KEY'):
        results.success("DeepSeek API key setting exists")
        if settings.DEEPSEEK_API_KEY:
            results.success(f"DeepSeek API key configured: {settings.DEEPSEEK_API_KEY[:10]}...")
        else:
            results.failure("DeepSeek API key", "API key is empty")
    else:
        results.failure("DeepSeek settings", "DEEPSEEK_API_KEY not found in config")
    
    if hasattr(settings, 'LLM_PROVIDER'):
        results.success(f"LLM Provider: {settings.LLM_PROVIDER}")
    else:
        results.failure("LLM Provider", "LLM_PROVIDER not found")
    
    if hasattr(settings, 'DATABASE_URL'):
        results.success("DATABASE_URL property exists")
    else:
        results.failure("DATABASE_URL", "Property not found")
        
except Exception as e:
    results.failure("Config import", str(e))


# ============================================================
# TEST 2: LLM Controller Module
# ============================================================
print("\n" + "=" * 70)
print(" TEST 2: LLM Controller Module")
print("=" * 70)

try:
    from llm_controller import (
        LLMController, 
        CommandHistory, 
        LLMProvider,
        llm_controller,
        generate_deceptive_response,
        get_controller_stats
    )
    
    results.success("LLM Controller imports")
    
    if hasattr(llm_controller, 'provider'):
        results.success(f"Controller provider: {llm_controller.provider.value}")
    else:
        results.failure("Controller provider", "Provider not set")
    
    if llm_controller.api_key:
        key_preview = llm_controller.api_key[:10] + "..." if len(llm_controller.api_key) > 10 else llm_controller.api_key
        results.success(f"API key set: {key_preview}")
    else:
        results.failure("API key", "No API key configured")
    
    history = CommandHistory()
    history.add_command("ls -la", "total 48\ndrwxr-xr-x...")
    context = history.get_context()
    if context and "ls -la" in context:
        results.success("CommandHistory works")
    else:
        results.failure("CommandHistory", "Context generation failed")
    
    static_response = llm_controller._static_fallback("whoami")
    if static_response == "www-data":
        results.success("Static fallback works")
    else:
        results.failure("Static fallback", f"Unexpected response: {static_response}")
    
except Exception as e:
    results.failure("LLM Controller", str(e))
    import traceback
    traceback.print_exc()


# ============================================================
# TEST 3: Merkle Tree Integrity Module
# ============================================================
print("\n" + "=" * 70)
print(" TEST 3: Merkle Tree Integrity Module")
print("=" * 70)

try:
    from integrity import (
        hash_log_entry,
        hash_pair,
        MerkleTree,
        MerkleLogger,
        merkle_logger
    )
    
    results.success("Integrity module imports")
    
    test_log = {
        "id": "test-123",
        "timestamp": "2024-01-15T10:30:00Z",
        "attacker_ip": "192.168.1.100",
        "command_entered": "ls -la",
        "response_sent": "total 48"
    }
    
    log_hash = hash_log_entry(test_log)
    if len(log_hash) == 64:
        results.success(f"hash_log_entry produces valid SHA-256: {log_hash[:16]}...")
    else:
        results.failure("hash_log_entry", f"Invalid hash length: {len(log_hash)}")
    
    hash1 = "a" * 64
    hash2 = "b" * 64
    combined = hash_pair(hash1, hash2)
    if len(combined) == 64:
        results.success("hash_pair works")
    else:
        results.failure("hash_pair", "Invalid combined hash")
    
    logs = [
        {"id": "1", "timestamp": "2024-01-01", "attacker_ip": "1.1.1.1", "command_entered": "cmd1", "response_sent": "resp1"},
        {"id": "2", "timestamp": "2024-01-02", "attacker_ip": "2.2.2.2", "command_entered": "cmd2", "response_sent": "resp2"},
        {"id": "3", "timestamp": "2024-01-03", "attacker_ip": "3.3.3.3", "command_entered": "cmd3", "response_sent": "resp3"},
        {"id": "4", "timestamp": "2024-01-04", "attacker_ip": "4.4.4.4", "command_entered": "cmd4", "response_sent": "resp4"},
    ]
    
    tree = MerkleTree(logs)
    if tree.root_hash:
        results.success(f"MerkleTree root hash: {tree.root_hash[:16]}...")
    else:
        results.failure("MerkleTree", "Failed to build tree")
    
    proof = tree.get_proof(0)
    if proof and len(proof) > 0:
        results.success(f"Merkle proof generated ({len(proof)} steps)")
    else:
        results.failure("Merkle proof", "Failed to generate proof")
    
    is_valid = MerkleTree.verify_proof(
        tree.leaf_hashes[0],
        proof,
        tree.root_hash
    )
    if is_valid:
        results.success("Merkle proof verification works")
    else:
        results.failure("Merkle verification", "Proof verification failed")
    
except Exception as e:
    results.failure("Integrity module", str(e))
    import traceback
    traceback.print_exc()


# ============================================================
# TEST 4: Edge Cases
# ============================================================
print("\n" + "=" * 70)
print(" TEST 4: Edge Cases")
print("=" * 70)

try:
    from integrity import MerkleTree, MerkleLogger, hash_log_entry
    
    empty_tree = MerkleTree([])
    if empty_tree.root_hash is None:
        results.success("Empty tree returns None root")
    else:
        results.failure("Empty tree", f"Expected None, got {empty_tree.root_hash}")
    
    single_log = [{"id": "1", "data": "test"}]
    single_tree = MerkleTree(single_log)
    if single_tree.root_hash:
        results.success("Single element tree works")
    else:
        results.failure("Single element tree", "Failed to build")
    
    odd_logs = [
        {"id": "1", "data": "a"},
        {"id": "2", "data": "b"},
        {"id": "3", "data": "c"}
    ]
    odd_tree = MerkleTree(odd_logs)
    if odd_tree.root_hash:
        results.success("Odd number of elements works")
    else:
        results.failure("Odd elements", "Failed to build")
    
    log_with_none = {
        "id": "test",
        "value": None,
        "other": "data"
    }
    hash_with_none = hash_log_entry(log_with_none)
    if hash_with_none:
        results.success("Handles None values in log data")
    else:
        results.failure("None handling", "Failed to hash")
    
except Exception as e:
    results.failure("Edge cases", str(e))


# ============================================================
# TEST 5: SQLAlchemy Models
# ============================================================
print("\n" + "=" * 70)
print(" TEST 5: SQLAlchemy Models")
print("=" * 70)

try:
    from models_sqlalchemy import (
        Base, Tenant, HoneypotLog, ReputationScore,
        AttackType, UserInput, GeoLocation, ClassificationResult
    )
    
    results.success("SQLAlchemy models import")
    
    tenant = Tenant(
        api_key="test_key_123",
        email="test@example.com",
        credit_balance=1000
    )
    results.success(f"Tenant model instantiation: {tenant.email}")
    
    rep_score = ReputationScore(
        ip_address="192.168.1.1",
        reputation_score=85
    )
    if rep_score.is_malicious(50):
        results.failure("ReputationScore", "IP should not be malicious at score 85")
    else:
        results.success("ReputationScore.is_malicious() works")
    
    new_score = rep_score.decrement_score(10)
    if new_score == 75:
        results.success("ReputationScore.decrement_score() works")
    else:
        results.failure("Decrement score", f"Expected 75, got {new_score}")
    
    attack_type = AttackType.SQLI
    results.success(f"AttackType enum works: {attack_type.value}")
    
except Exception as e:
    results.failure("SQLAlchemy models", str(e))
    import traceback
    traceback.print_exc()


# ============================================================
# TEST 6: Database Module (Mock/Structure Test)
# ============================================================
print("\n" + "=" * 70)
print(" TEST 6: Database Module Structure")
print("=" * 70)

try:
    from database_postgres import (
        Database, DatabaseSettings, db, get_db, get_db_context,
        create_tenant, get_tenant_by_api_key, save_honeypot_log,
        get_honeypot_logs, get_or_create_reputation_score
    )
    
    results.success("Database module imports")
    
    db_settings = DatabaseSettings()
    if db_settings.database_url:
        results.success("DatabaseSettings.database_url works")
    else:
        results.failure("DatabaseSettings", "database_url not configured")
    
    if db_settings.sync_database_url:
        results.success("DatabaseSettings.sync_database_url works")
    else:
        results.failure("DatabaseSettings", "sync_database_url not configured")
    
except Exception as e:
    results.failure("Database module", str(e))
    import traceback
    traceback.print_exc()


# ============================================================
# TEST 7: DeepSeek API Integration (Real Test)
# ============================================================
print("\n" + "=" * 70)
print(" TEST 7: DeepSeek API Integration")
print("=" * 70)

async def test_deepseek_api():
    try:
        from llm_controller import llm_controller
        
        if not llm_controller.api_key:
            results.failure("DeepSeek API", "No API key configured")
            return
        
        response = await llm_controller._static_fallback("whoami")
        if response:
            results.success("Static fallback returns response")
        
        print("   🔄 Testing actual API call (this may take a moment)...")
        
        try:
            api_response = await llm_controller.call_llm_api("Respond with: hello")
            if api_response and len(api_response) > 0:
                results.success(f"API call successful: {api_response[:50]}...")
            else:
                results.failure("API call", "Empty response")
        except Exception as api_error:
            if "timed out" in str(api_error).lower():
                results.failure("API call", "Request timed out")
            else:
                results.failure("API call", str(api_error))
        
        stats = get_controller_stats()
        results.success(f"Stats: {stats['successful_requests']} successful, {stats['failed_requests']} failed")
        
    except Exception as e:
        results.failure("DeepSeek API test", str(e))
        import traceback
        traceback.print_exc()

asyncio.run(test_deepseek_api())


# ============================================================
# TEST 8: Merkle Logger Integration
# ============================================================
print("\n" + "=" * 70)
print(" TEST 8: Merkle Logger Integration")
print("=" * 70)

try:
    from integrity import MerkleLogger
    
    logger = MerkleLogger()
    
    class MockLog:
        def __init__(self, id, cmd):
            self.id = id
            self.timestamp = datetime.utcnow()
            self.attacker_ip = "1.2.3.4"
            self.command_entered = cmd
            self.response_sent = "response"
            self.metadata = {}
        
        def to_dict(self):
            return {
                "id": str(self.id),
                "timestamp": self.timestamp.isoformat(),
                "attacker_ip": self.attacker_ip,
                "command_entered": self.command_entered,
                "response_sent": self.response_sent,
                "metadata": self.metadata
            }
    
    mock_logs = [MockLog(i, f"cmd{i}") for i in range(5)]
    
    hashes = logger.add_logs(mock_logs)
    if len(hashes) == 5:
        results.success("MerkleLogger.add_logs() handles objects with to_dict()")
    else:
        results.failure("MerkleLogger", f"Expected 5 hashes, got {len(hashes)}")
    
    root = logger.build_tree()
    if root:
        results.success(f"MerkleLogger.build_tree() works: {root[:16]}...")
    else:
        results.failure("MerkleLogger.build_tree", "Failed to build tree")
    
    stats = logger.get_stats()
    if stats["log_count"] == 5:
        results.success("MerkleLogger stats correct")
    else:
        results.failure("MerkleLogger stats", f"Expected 5 logs, got {stats['log_count']}")
    
except Exception as e:
    results.failure("Merkle Logger integration", str(e))
    import traceback
    traceback.print_exc()


# ============================================================
# FINAL SUMMARY
# ============================================================
success = results.summary()

if success:
    print("\n🎉 ALL TESTS PASSED!")
    sys.exit(0)
else:
    print("\n⚠️  SOME TESTS FAILED - See above for details")
    sys.exit(1)
