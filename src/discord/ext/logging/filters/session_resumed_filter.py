import logging
from logging import INFO


class SessionResumedFilter(logging.Filter):
    def filter(self, record: logging.LogRecord):
        return not (
            "has successfully RESUMED session" in record.message
            and record.levelno == INFO
        )
