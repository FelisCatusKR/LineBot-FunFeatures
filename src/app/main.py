import re

from linebot import WebhookHandler
from linebot.models import MessageEvent, TextMessage
from linebot.exceptions import LineBotApiError, InvalidSignatureError

from .config import LINEBOT_SECRET, CELEBRATING_TARGET, logger
from .leaderboard import celebrating_birthday, leaderboard


handler = WebhookHandler(LINEBOT_SECRET)


@handler.add(MessageEvent, message=TextMessage)
def message(line_event):
    p1 = re.compile(CELEBRATING_TARGET)
    p2 = re.compile("생일")
    text = line_event.message.text
    if p1.search(text) and p2.search(text):
        celebrating_birthday(line_event)
    elif text == "!순위":
        leaderboard(line_event)


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
