import asyncio
import logging
import os

from discord.ext.commands import Bot

import discord

from .. import get_user_log_handler

wildbush_id = 704773768035172726


def main():
    asyncio.run(_main())


def test_logs(logger: logging.Logger):
    logger.debug("DEBUG!")
    logger.info("SOME INFO")
    logger.warning("WARNING, THIS IS A TEST")
    logger.error("ERROR, WITHOUT AN EXCEPTION")
    logger.critical("THIS IS CRITICAL")
    logger.log(
        level=logging.ERROR,
        msg="ERROR WITH AN EXCEPTION",
        exc_info=Exception("This is an error"),
    )


async def _main():
    bot = Bot("!", intents=discord.Intents.default())
    token = os.getenv("DISCORD_TOKEN")

    # setup logger
    logger = logging.getLogger()
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    discord_handler = get_user_log_handler(bot, wildbush_id)
    logger.addHandler(discord_handler)

    # TEST
    logger.info("Starting Test!")
    task = asyncio.create_task(bot.start(token))
    await asyncio.sleep(1)
    await bot.wait_until_ready()

    test_logs(logger)
    logger.info("RAPID TEST")
    for i in range(10):
        logger.info(f"RAPID -> {i}")

    logger.info("TEST DONE")
    await task
    # await bot.close()
