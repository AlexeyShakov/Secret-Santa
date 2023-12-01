import asyncio

from src.config import DP, BOT


async def main() -> None:
    print("Бот запущен")
    await DP.start_polling(BOT)


if __name__ == "__main__":
    asyncio.run(main())
