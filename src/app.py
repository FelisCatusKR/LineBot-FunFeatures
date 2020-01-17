import os
import sys
import logging
import re

from linebot import LineBotApi, WebhookHandler
from linebot.models import (
    MessageEvent,
    TextMessage,
    TextSendMessage,
)
from linebot.exceptions import LineBotApiError, InvalidSignatureError

logger = logging.getLogger()
logger.setLevel(logging.ERROR)

LINEBOT_SECRET = os.getenv("LINEBOT_SECRET", None)
LINEBOT_ACCESS_TOKEN = os.getenv("LINEBOT_ACCESS_TOKEN", None)
if LINEBOT_SECRET is None:
    logger.error("Specify LINEBOT_SECRET as environment variable.")
    sys.exit(1)
if LINEBOT_ACCESS_TOKEN is None:
    logger.error("Specify LINEBOT_ACCESS_TOKEN as environment variable.")
    sys.exit(1)

line_bot_api = LineBotApi(LINEBOT_ACCESS_TOKEN)
handler = WebhookHandler(LINEBOT_SECRET)

CELEBRATING_TARGET = os.environ["CELEBRATING_TARGET"]
p1 = re.compile(CELEBRATING_TARGET)
p2 = re.compile("생일")


@handler.add(MessageEvent, message=TextMessage)
def message(line_event):
    text = line_event.message.text
    if p1.search(text) and p2.search(text):
        line_bot_api.reply_message(line_event.reply_token, TextSendMessage("🎉"))


def response(event, context):
    signature = event["headers"]["X-Line-Signature"]
    body = event["body"]
    ok_json = {"isBase64Encoded": False, "statusCode": 200, "headers": {}, "body": ""}
    error_json = {
        "isBase64Encoded": False,
        "statusCode": 403,
        "headers": {},
        "body": "Error",
    }

    try:
        handler.handle(body, signature)
    except LineBotApiError as e:
        logger.error("Got exception from LINE Messaging API: %s\n" % e.message)
        for m in e.error.details:
            logger.error("  %s: %s" % (m.property, m.message))
        return error_json
    except InvalidSignatureError:
        return error_json

    return ok_json
