import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


def send_email(suggestions: List[Dict[str, str]]) -> None:
    logger.info("Send email invoked")
