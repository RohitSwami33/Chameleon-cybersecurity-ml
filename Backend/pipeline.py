import asyncio
import logging
from bilstm_inference import bilstm_model
from local_inference import mlx_model

logger = logging.getLogger(__name__)

async def evaluate_payload(payload: str) -> str:
    """
    Two-Stage Evaluation Pipeline:
    Stage 1 (Fast Filter): BiLSTM model provides an anomaly score.
    Stage 2 (Deep Analysis): Local MLX LLM model provides final BLOCK/ALLOW verdict.
    """
    # Stage 1: Fast Filter (BiLSTM)
    bilstm_score = await asyncio.to_thread(bilstm_model.predict, payload)
    logger.info(f"Pipeline Stage 1 [BiLSTM]: Anomaly score for payload is {bilstm_score:.4f}")

    # Note: Future optimization threshold logic
    # If the BiLSTM score is e.g. < 0.05 (95% confident it's safe), 
    # we could immediately return "ALLOW" to save MLX compute.
    # if bilstm_score < 0.05:
    #     logger.info("Pipeline Stage 1 [BiLSTM]: Highly confident benign. Bypassing MLX.")
    #     return "ALLOW"
    
    # Stage 2: Deep Analysis (Local MLX LLM)
    mlx_verdict = await mlx_model.infer(payload)
    logger.info(f"Pipeline Stage 2 [MLX]: Verdict is {mlx_verdict}")

    # The final authoritative verdict comes from the MLX model
    return mlx_verdict
