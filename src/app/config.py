import logging
import os
import sys

logger = logging.getLogger()
logger.setLevel(logging.ERROR)

LINEBOT_SECRET = os.getenv("LINEBOT_SECRET")
LINEBOT_ACCESS_TOKEN = os.getenv("LINEBOT_ACCESS_TOKEN")
if LINEBOT_SECRET is None:
    logger.error("Specify LINEBOT_SECRET as environment variable.")
    sys.exit(1)
if LINEBOT_ACCESS_TOKEN is None:
    logger.error("Specify LINEBOT_ACCESS_TOKEN as environment variable.")
    sys.exit(1)

CELEBRATING_TARGET = os.getenv("CELEBRATING_TARGET")
