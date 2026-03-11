"""
Chameleon Two-Stage Evaluation Pipeline with Meta-Heuristic Optimization
=========================================================================
Integrates:
  - Heuristic classifier for benign detection
  - Balanced MLX LLM for malicious classification
  - PSO for adaptive tarpitting
  - GA for dynamic deception schema evolution

Hardened with Algorithm B — Multi-Layer Normalisation + VAC Classifier:
  - NormalisationPipeline.normalise() runs FIRST (7-pass canonicalisation)
  - BehaviourClassifier detects SCANNER/FUZZER and short-circuits them
  - BiLSTM/MLX receive normalised payload, not raw
  - Original payload preserved in _last_raw_payload for logging
"""

import asyncio
import logging
from bilstm_inference import bilstm_model
from local_inference import mlx_model
from ml_classifier import classifier

logger = logging.getLogger(__name__)

# ── Algorithm B: Import normalisation and behaviour classification ─────
try:
    from normalisation_pipeline import normalisation_pipeline
    _NORMALISER_AVAILABLE = True
except ImportError:
    _NORMALISER_AVAILABLE = False
    logger.warning("NormalisationPipeline not available — using raw payloads")

try:
    from behaviour_classifier import behaviour_classifier, AttackerClass
    _BEHAVIOUR_CLASSIFIER_AVAILABLE = True
except ImportError:
    _BEHAVIOUR_CLASSIFIER_AVAILABLE = False
    logger.warning("BehaviourClassifier not available — treating all as HUMAN")

# Module-level storage for last raw/normalised payloads (for logging)
_last_raw_payload: str = ""
_last_normalised_payload: str = ""
_last_attacker_class: str = "HUMAN"


def get_last_payload_info() -> dict:
    """Return info about the last processed payload (for logging by callers)."""
    return {
        "raw_payload": _last_raw_payload,
        "normalised_payload": _last_normalised_payload,
        "attacker_class": _last_attacker_class,
    }


async def evaluate_payload(payload: str, ip_address: str = "unknown") -> str:
    """
    Multi-Stage Evaluation Pipeline:

    Stage 0 (NEW - Algorithm B): Normalise payload (7-pass canonicalisation)
    Stage 0.5 (NEW - Algorithm B): Behaviour classification (SCANNER/FUZZER/HUMAN)
    Stage 1 (Fast Filter): Heuristic classifier provides attack type detection.
    Stage 2 (Deep Analysis): Balanced MLX LLM model provides final BLOCK/ALLOW verdict.

    For reliable benign user detection, we use the heuristic classifier as primary.
    The balanced model (retrained on 2930 samples with 50/50 distribution) reduces false positives.

    SCANNER → always returns BLOCK but short-circuits LLM (stage-1 loop)
    FUZZER  → always returns BLOCK but short-circuits LLM (junk response)
    HUMAN   → full pipeline as before
    """
    global _last_raw_payload, _last_normalised_payload, _last_attacker_class

    _last_raw_payload = payload

    # ── Stage 0: Normalisation (Algorithm B) ──────────────────────────
    if _NORMALISER_AVAILABLE:
        normalised = normalisation_pipeline.normalise(payload)
        logger.info(f"Pipeline Stage 0 [Normalisation]: len={len(payload)}->{len(normalised)}")
    else:
        normalised = payload
    _last_normalised_payload = normalised

    # ── Stage 0.5: Behaviour Classification (Algorithm B) ─────────────
    if _BEHAVIOUR_CLASSIFIER_AVAILABLE:
        attacker_class = behaviour_classifier.classify(ip_address, normalised)
        _last_attacker_class = attacker_class.value
        logger.info(f"Pipeline Stage 0.5 [Behaviour]: {attacker_class.value}")

        if attacker_class == AttackerClass.SCANNER:
            logger.info("Pipeline: SCANNER detected — short-circuiting to BLOCK (stage-1 loop)")
            return "BLOCK"

        if attacker_class == AttackerClass.FUZZER:
            logger.info("Pipeline: FUZZER detected — short-circuiting to BLOCK (junk response)")
            return "BLOCK"
    else:
        _last_attacker_class = "HUMAN"

    # ── Stage 1: Heuristic Classification (reliable for benign detection) ──
    # Now receives normalised payload (Algorithm B: avoid double-processing)
    classification = classifier.classify(normalised)
    logger.info(f"Pipeline Stage 1 [Heuristic]: Type={classification.attack_type.value}, Malicious={classification.is_malicious}")

    # If heuristic says benign, trust it (avoids any ML false positives)
    if not classification.is_malicious:
        logger.info("Pipeline Stage 1 [Heuristic]: Benign input detected. Returning ALLOW.")
        return "ALLOW"

    # ── Stage 2: Deep Analysis (Balanced MLX LLM) for potentially malicious inputs ──
    # Also receives normalised payload
    mlx_verdict = await mlx_model.infer(normalised)
    logger.info(f"Pipeline Stage 2 [MLX-Balanced]: Verdict is {mlx_verdict}")

    # The final authoritative verdict comes from the MLX model for malicious inputs
    return mlx_verdict
