from pathlib import Path

import uvicorn

from giveaway_bot.common.logging import setup_logging
from giveaway_bot.config import build_config
from giveaway_bot.presentation.api.run import main

setup_logging()


def run():
    config = build_config(Path("./config.toml"))
    app = main(config=config)
    uvicorn.run(
        app,
        host="0.0.0.0",  # noqa: S104
        port=80,
    )


if __name__ == "__main__":
    run()
