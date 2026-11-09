from typing import override

from discord.abc import Messageable
from discord.ext.commands import Bot

from discord import Client, HTTPException, NotFound, User

from ..filters.rate_limit_filter import RateLimitFilter
from ..filters.session_resumed_filter import SessionResumedFilter
from .base_discord_handler import BaseDiscordHandler


class UserLogHandler(BaseDiscordHandler):
    def __init__(self, discord_client: Client, target_user_id: int):
        self._target_user_id: int = target_user_id
        self._channel: User | None = None

        super().__init__(discord_client)

    @override
    async def _setup(self) -> Messageable:
        try:
            self._target_user = await self._client.fetch_user(self._target_user_id)
            return await self._target_user.create_dm()

        except NotFound:
            self._logger.error(
                f"User : {self._target_user_id} could not be found for logging!"
            )
            return None
        except HTTPException:
            self._logger.error("Failed to fetch user for logger!")
            return None


def get_user_log_handler(discord_client: Bot, target_user_id: int):
    handler = UserLogHandler(discord_client, target_user_id)
    handler.addFilter(RateLimitFilter())
    handler.addFilter(SessionResumedFilter())
    return handler
