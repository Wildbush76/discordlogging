from discord.ext import logging

from ..filters.rate_limit_filter import RateLimitFilter
from ..filters.session_resumed_filter import SessionResumedFilter
from .base_discord_handler import BaseDiscordHandler


class ChannelLogHandler(BaseDiscordHandler):
    def __init__(self, discord_client: logging.Client, target_channel_id: int):
        self._target_channel_id: int = target_channel_id
        self._target_channel: logging.User | None = None

        super().__init__(discord_client)

    async def _setup(self) -> bool:
        try:
            self._target_channel = self._client.fetch_channel(self.target_channel_id)
            return True
        except logging.NotFound:
            self._logger.error(
                f"Channel : {self.target_channel_id} could not be found for logging!"
            )
            return False
        except logging.HTTPException:
            self._logger.error("Failed to fetch channel for logger!")
            return False

    async def _send_message(self, embed: logging.Embed):
        await self._target_channel.send(embed=embed)


def get_channel_log_handler(
    discord_client: logging.Client, target_channel_id: int
) -> ChannelLogHandler:
    handler = ChannelLogHandler(discord_client, target_channel_id)
    handler.addFilter(RateLimitFilter())
    handler.addFilter(SessionResumedFilter())
    return handler
