import sys
import asyncio

# Setup path so imports work
import os
sys.path.append(os.path.abspath('/Users/rohit/Documents/Sem-4_project/Chameleon-cybersecurity-ml/Backend'))

from src.api.pipeline import evaluate_payload

async def main():
    payload = "LOGIN:SELECT * FROM users WHERE '1'='1'"
    verdict = await evaluate_payload(payload)
    print(f"Payload: {payload}")
    print(f"Verdict: {verdict}")

if __name__ == "__main__":
    asyncio.run(main())
