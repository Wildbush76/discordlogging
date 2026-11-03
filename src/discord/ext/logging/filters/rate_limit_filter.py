import logging
from logging import WARNING


class RateLimitFilter(logging.Filter):
    def filter(self, record: logging.LogRecord):
        return not (
            "responded with 429" in record.message and record.levelno == WARNING
        )
