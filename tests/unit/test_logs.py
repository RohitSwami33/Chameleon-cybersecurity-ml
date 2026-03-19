import asyncio
from database import get_attack_logs
from models import AttackLog

async def main():
    logs = await get_attack_logs(0, 3)
    print("Logs retrieved:", len(logs))
    for i, log in enumerate(logs):
        try:
            print("Row", i, log["id"])
            AttackLog(**log)
        except Exception as e:
            print("Validation error on row", i)
            import traceback
            traceback.print_exc()
            print("Data:", log)
            break

if __name__ == "__main__":
    asyncio.run(main())
