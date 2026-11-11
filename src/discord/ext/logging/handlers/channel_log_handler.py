from discord import Client, HTTPException, NotFound

from ..filters.rate_limit_filter import RateLimitFilter
from ..filters.session_resumed_filter import SessionResumedFilter
from .base_discord_handler import BaseDiscordHandler


class ChannelLogHandler(BaseDiscordHandler):
    def __init__(self, discord_client: Client, target_channel_id: int):
        self._target_channel_id: int = target_channel_id

        super().__init__(discord_client)

    async def _setup(self) -> bool:
        try:
            channel = await self._client.fetch_channel(self._target_channel_id)
            return channel
        except NotFound:
            self._logger.error(
                f"Channel : {self._target_channel_id} could not be found for logging!"
            )
            return None
        except HTTPException:
            self._logger.error("Failed to fetch channel for logger!")
            return None


def get_channel_log_handler(
    discord_client: Client, target_channel_id: int
) -> ChannelLogHandler:
    handler = ChannelLogHandler(discord_client, target_channel_id)
    handler.addFilter(RateLimitFilter())
    handler.addFilter(SessionResumedFilter())
    return handler
