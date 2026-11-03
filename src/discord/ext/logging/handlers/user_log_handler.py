from typing import override

from discord.ext import logging

from ..filters.rate_limit_filter import RateLimitFilter
from ..filters.session_resumed_filter import SessionResumedFilter
from .base_discord_handler import BaseDiscordHandler


class UserLogHandler(BaseDiscordHandler):
    def __init__(self, discord_client: logging.Client, target_user_id: int):
        self._target_user_id: int = target_user_id
        self._target_user: logging.User | None = None

        super().__init__(discord_client)

    @override
    async def _setup(self) -> bool:
        try:
            self._target_user = await self._client.fetch_user(self.target_user_id)
            return True
        except logging.NotFound:
            self._logger.error(
                f"User : {self.target_user_id} could not be found for logging!"
            )
            return False
        except logging.HTTPException:
            self._logger.error("Failed to fetch user for logger!")
            return False

    @override
    async def _send_message(self, embed: logging.Embed):
        await self._target_user.send(embed=embed)


def get_user_log_handler(discord_client: logging.Client, target_user_id: int):
    handler = UserLogHandler(discord_client, target_user_id)
    handler.addFilter(RateLimitFilter())
    handler.addFilter(SessionResumedFilter())
    return handler
