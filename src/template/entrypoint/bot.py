import asyncio
from pathlib import Path

from template.common.logging import setup_logging
from template.config import build_config
from template.presentation.bot.run import run_telegram_bot

setup_logging()

async def main():
    config = build_config(Path("./config.toml"))
    await run_telegram_bot(config)

if __name__ == "__main__":
    asyncio.run(main())
