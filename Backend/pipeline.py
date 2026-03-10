import asyncio
import logging
from bilstm_inference import bilstm_model
from local_inference import mlx_model
from ml_classifier import classifier

logger = logging.getLogger(__name__)

async def evaluate_payload(payload: str) -> str:
    """
    Two-Stage Evaluation Pipeline:
    Stage 1 (Fast Filter): Heuristic classifier provides attack type detection.
    Stage 2 (Deep Analysis): Balanced MLX LLM model provides final BLOCK/ALLOW verdict.

    For reliable benign user detection, we use the heuristic classifier as primary.
    The balanced model (retrained on 2930 samples with 50/50 distribution) reduces false positives.
    """
    # Stage 1: Heuristic Classification (reliable for benign detection)
    classification = classifier.classify(payload)
    logger.info(f"Pipeline Stage 1 [Heuristic]: Type={classification.attack_type.value}, Malicious={classification.is_malicious}")

    # If heuristic says benign, trust it (avoids any ML false positives)
    if not classification.is_malicious:
        logger.info("Pipeline Stage 1 [Heuristic]: Benign input detected. Returning ALLOW.")
        return "ALLOW"

    # Stage 2: Deep Analysis (Balanced MLX LLM) for potentially malicious inputs
    mlx_verdict = await mlx_model.infer(payload)
    logger.info(f"Pipeline Stage 2 [MLX-Balanced]: Verdict is {mlx_verdict}")

    # The final authoritative verdict comes from the MLX model for malicious inputs
    return mlx_verdict
