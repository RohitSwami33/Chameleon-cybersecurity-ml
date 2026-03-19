#!/usr/bin/env python3
"""
Chameleon Connection Audit Script
=================================
Verifies all module connections and imports are properly configured.
Run this to ensure the entire pipeline is connected correctly.

Usage:
    python verify_connections.py
"""

import sys
import os
from pathlib import Path

# Add Backend to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 70)
print("CHAMELEON CONNECTION AUDIT")
print("=" * 70)

# Track results
results = {
    "passed": [],
    "failed": [],
    "warnings": []
}

def check_import(module_path, description):
    """Check if a module can be imported."""
    try:
        __import__(module_path)
        results["passed"].append(f"✅ {description}")
        print(f"✅ {description}")
        return True
    except ImportError as e:
        results["failed"].append(f"❌ {description}: {e}")
        print(f"❌ {description}: {e}")
        return False
    except Exception as e:
        results["warnings"].append(f"⚠️  {description}: {e}")
        print(f"⚠️  {description}: {e}")
        return False

def check_file_exists(file_path, description):
    """Check if a file exists."""
    if os.path.exists(file_path):
        results["passed"].append(f"✅ {description}")
        print(f"✅ {description}")
        return True
    else:
        results["failed"].append(f"❌ {description}: {file_path}")
        print(f"❌ {description}: {file_path}")
        return False

print("\n1. CORE MODULES")
print("-" * 70)
check_import("src.core.config", "Core Config")
check_import("src.core.database", "Core Database (MongoDB)")
check_import("src.core.database_postgres", "Core Database (PostgreSQL)")
check_import("src.core.models", "Core Models (Pydantic)")
check_import("src.core.models_sqlalchemy", "Core Models (SQLAlchemy)")

print("\n2. ML ENGINE")
print("-" * 70)
check_import("src.ml_engine.bilstm_inference", "BiLSTM Inference")
check_import("src.ml_engine.local_inference", "Local MLX Inference")
check_import("src.ml_engine.ml_classifier", "ML Classifier")
check_import("src.ml_engine.inference", "ML Inference")
check_import("src.ml_engine.simple_tokenizer", "Simple Tokenizer")

print("\n3. API MODULES")
print("-" * 70)
check_import("src.api.auth", "API Auth")
check_import("src.api.pipeline", "API Pipeline")
check_import("src.api.main", "API Main (FastAPI)")

print("\n4. UTILITIES")
print("-" * 70)
check_import("src.utils.alert_manager", "Alert Manager")
check_import("src.utils.attacker_session", "Attacker Session")
check_import("src.utils.blockchain_logger", "Blockchain Logger")
check_import("src.utils.deception_engine", "Deception Engine")
check_import("src.utils.deception_engine_v2", "Deception Engine V2")
check_import("src.utils.integrity", "Integrity Hashing")
check_import("src.utils.tarpit_manager", "Tarpit Manager")
check_import("src.utils.threat_score", "Threat Score")
check_import("src.utils.threat_intel_service", "Threat Intel Service")
check_import("src.utils.chatbot_service", "Chatbot Service")

print("\n5. OPTIMIZATION (Meta-Heuristics)")
print("-" * 70)
check_import("src.optimization.meta_heuristics", "Meta-Heuristics (PSO + GA)")

print("\n6. FILE EXISTENCE CHECKS")
print("-" * 70)
check_file_exists('models/bilstm/chameleon_lstm_m4_50k.pth', "BiLSTM Model File")
check_file_exists('models/char_cnn_gru/chameleon_char_cnn_gru.keras', "Keras CNN-GRU Model")
check_file_exists("src/ml_engine/bilstm_inference.py", "BiLSTM Inference Code")
check_file_exists("src/ml_engine/local_inference.py", "MLX Inference Code")
check_file_exists("src/optimization/meta_heuristics.py", "Meta-Heuristics Code")

print("\n7. PIPELINE INTEGRATION")
print("-" * 70)

try:
    from src.api.pipeline import evaluate_payload
    print("✅ Pipeline evaluate_payload imported")
    results["passed"].append("Pipeline evaluate_payload")
except Exception as e:
    print(f"❌ Pipeline evaluate_payload: {e}")
    results["failed"].append(f"Pipeline evaluate_payload: {e}")

try:
    from src.optimization.meta_heuristics import pso_optimizer, ga_optimizer, session_tracker
    print("✅ Meta-heuristics optimizers imported")
    results["passed"].append("Meta-heuristics optimizers")
except Exception as e:
    print(f"❌ Meta-heuristics optimizers: {e}")
    results["failed"].append(f"Meta-heuristics optimizers: {e}")

print("\n" + "=" * 70)
print("AUDIT SUMMARY")
print("=" * 70)
print(f"✅ Passed: {len(results['passed'])}")
print(f"❌ Failed: {len(results['failed'])}")
print(f"⚠️  Warnings: {len(results['warnings'])}")

if results["failed"]:
    print("\n❌ FAILED CHECKS:")
    for failure in results["failed"]:
        print(f"  {failure}")

if results["warnings"]:
    print("\n⚠️  WARNINGS:")
    for warning in results["warnings"]:
        print(f"  {warning}")

print("\n" + "=" * 70)

if not results["failed"] and not results["warnings"]:
    print("🎉 ALL CONNECTIONS VERIFIED SUCCESSFULLY!")
    sys.exit(0)
elif not results["failed"]:
    print("⚠️  Some warnings detected. Review above.")
    sys.exit(1)
else:
    print("❌ CRITICAL: Some connections failed. Fix before deployment.")
    sys.exit(1)
