import asyncio
from abc import ABC, abstractmethod
from logging import Handler, LogRecord, getLogger
from typing import Final, override

from discord.abc import Messageable
from discord.ext.commands import Bot
from ratelimit import limits, sleep_and_retry

import discord
from discord import Embed


class BaseDiscordHandler(Handler, ABC):
    MAX_DESCRIPTION_LENGTH: Final[int] = 4096
    MAX_TITLE_LENGTH: Final[int] = 256

    def __init__(self, client: Bot, level: int = 0):
        super().__init__(level=0)
        self._ready = asyncio.Event()
        self._client: Bot = client
        self._logger = getLogger(self.__class__.__name__)
        self.__channel: Messageable | None = None
        client.add_listener(self.__setup, "on_ready")

    async def __setup(self):
        await self._client.wait_until_ready()
        if self.__channel is None:
            self.__channel = await self._setup()
        self._ready.set()

    @abstractmethod
    async def _setup(self) -> Messageable | None:
        pass

    @sleep_and_retry
    @limits(calls=1, period=1)
    async def _send_message(self, embed: Embed):
        self._logger.debug(f"Sending message! {embed.description}")
        await self.__channel.send(embed=embed)

    @override
    def emit(self, record: LogRecord) -> None:
        asyncio.create_task(self._send_record(record))

    async def info(self, title: str, message: str):
        await self._send_message(
            Embed(title=title, description=message, color=discord.Color.blue())
        )

    async def warning(self, title: str, message: str):
        await self._send_message(
            Embed(title=title, description=message, color=discord.Color.yellow())
        )

    async def error(self, title: str, message: str):
        await self._send_message(
            Embed(title=title, description=message, color=discord.Color.red())
        )

    async def critical(self, title: str, message: str):
        await self._send_message(
            Embed(title=title, description=message, color=discord.Color.dark_red())
        )

    async def _send_record(self, record: LogRecord) -> None:
        await self._ready.wait()
        if self.__channel is None or self._client.is_closed():
            return

        title = f"{record.name}:{record.levelname}"
        description = record.message

        if len(description) > self.MAX_DESCRIPTION_LENGTH:
            self.warning(
                self.__class__.__name__, " Message description too long, truncating"
            )
            description = description[0 : self.MAX_DESCRIPTION_LENGTH]

        if len(title) > self.MAX_TITLE_LENGTH:
            self.warning(self.__class__.__name__, "Message title too long, truncating")
            title = title[0 : self.MAX_TITLE_LENGTH]

        if record.exc_text is not None:
            description += f" -> {record.exc_text}"

        match record.levelname.upper():
            case "INFO":
                await self.info(title, description)
            case "WARNING":
                await self.warning(title, description)
            case "ERROR":
                await self.error(title, description)
            case "CRITICAL":
                await self.critical(title, description)
