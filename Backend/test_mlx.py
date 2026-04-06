import asyncio
from src.ml_engine.local_inference import mlx_model

async def main():
    res = await mlx_model.infer("admin' OR '1'='1")
    print("Inference Result:", res)

asyncio.run(main())
