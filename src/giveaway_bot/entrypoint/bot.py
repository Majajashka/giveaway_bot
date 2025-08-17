import asyncio
from pathlib import Path

from giveaway_bot.common.logging import setup_logging
from giveaway_bot.config import build_config
from giveaway_bot.presentation.bot.run import run_telegram_bot

setup_logging(level=0)  # Set logging level to DEBUG for detailed output

async def main():
    config = build_config(Path("./config.toml"))
    await run_telegram_bot(config)

if __name__ == "__main__":
    asyncio.run(main())
