from linebot.exceptions import LineBotApiError, InvalidSignatureError

from app import handler
from app.config import logger


def response(event, context):
    line_header = "X-Line-Signature".lower()
    signature = event["headers"][line_header]
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
    else:
        return ok_json
