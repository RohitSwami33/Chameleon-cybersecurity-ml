import asyncio
from database_postgres import db
from database import get_attack_logs
from models import AttackLog

async def main():
    await db.connect()
    print("DB Connected")
    try:
        logs = await get_attack_logs(0, 3)
        print("Logs retrieved:", len(logs))
        for i, log in enumerate(logs):
            try:
                print("Row", i, log["id"])
                AttackLog(**log)
                print("Row", i, "Valid")
            except Exception as e:
                print("Validation error on row", i)
                import traceback
                traceback.print_exc()
                print("Data:", log)
                break
    finally:
        await db.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
