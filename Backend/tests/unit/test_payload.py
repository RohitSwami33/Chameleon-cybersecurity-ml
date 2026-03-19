import sys
import asyncio

# Setup path so imports work
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.api.pipeline import evaluate_payload

async def main():
    payload = "LOGIN:SELECT * FROM users WHERE '1'='1'"
    verdict = await evaluate_payload(payload)
    print(f"Payload: {payload}")
    print(f"Verdict: {verdict}")

if __name__ == "__main__":
    asyncio.run(main())
