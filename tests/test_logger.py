from discord.ext.logging import get_user_log_handler  # type: ignore # noqa
import discord.ext.test as dpytest
import pytest_asyncio
import discord
import logging


@pytest_asyncio.fixture
async def bot():
    bot = discord.Client()
    dpytest.configure(bot)
    yield bot


@pytest_asyncio.fixture
async def logger():
    log = logging.getLogger()
    log.setLevel(logging.INFO)
    yield log


@pytest_asyncio.fixture
async def user_logger(bot: discord.Client, logger: logging.Logger):
    handler = get_user_log_handler(bot, 0)
    logger.addHandler(handler)
    yield


async def test_just_print():
    print("yeah")
    assert 1 == 1
