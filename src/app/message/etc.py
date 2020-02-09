import random

from linebot.models import TextSendMessage

from . import line_bot_api, exception_handler


@exception_handler
def select_random_item(line_event, args: str):
    items = args.split("|")
    if len(items) < 2:
        line_bot_api.reply_message(
            line_event.reply_token,
            TextSendMessage("무작위 선택 도중 오류가 발생했습니다: 최소한 두 개 이상의 항목을 제공해야 합니다."),
        )
    else:
        line_bot_api.reply_message(
            line_event.reply_token, TextSendMessage(random.choice(items))
        )
