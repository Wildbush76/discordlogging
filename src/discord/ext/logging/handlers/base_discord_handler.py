import asyncio
from abc import ABC, abstractmethod
from logging import Handler, LogRecord, getLogger
from typing import override

from ratelimit import limits, sleep_and_retry

import discord
from discord import Client, Embed


class BaseDiscordHandler(Handler, ABC):
    def __init__(self, client: Client, level: int = 0):
        super().__init__(level=0)
        self._ready = asyncio.Event()
        self._successful = False
        self._client: Client = client
        self._logger = getLogger(self.__class__.__name__)
        asyncio.create_task(self.__setup())

    async def __setup(self):
        await self._client.wait_until_ready()
        self._successful = await self._setup()
        self._ready.set()

    @abstractmethod
    async def _setup(self) -> bool:
        pass

    @abstractmethod
    async def _send_message(self, embed: Embed):
        pass

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

    @sleep_and_retry
    @limits(calls=1, period=0.5)
    async def _send_record(self, record: LogRecord) -> None:
        await self._ready.wait()
        if self._successful is None or self._client.is_closed():
            return

        title = f"{record.name}:{record.levelname}"
        description = record.message

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
