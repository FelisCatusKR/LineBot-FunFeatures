from functools import wraps

from linebot import LineBotApi
from linebot.models import TextSendMessage

from app.config import LINEBOT_ACCESS_TOKEN, LINE_USER_ID

line_bot_api = LineBotApi(LINEBOT_ACCESS_TOKEN)


def exception_handler(original_function):
    @wraps(original_function)
    def wrapper_function(event=None, *args, **kwargs):
        try:
            return original_function(event, *args, **kwargs)
        except Exception as e:
            line_bot_api.push_message(
                LINE_USER_ID,
                TextSendMessage(
                    text=(
                        "전달된 명령어 : "
                        + event.message.text
                        + "\nexception detail : "
                        + e.__str__()
                    )
                ),
            )

    return wrapper_function


@exception_handler
def send_help_message(line_event, args: str):
    line_bot_api.reply_message(
        line_event.reply_token, TextSendMessage("준비중입니다."),
    )


@exception_handler
def send_error_message(line_event, command: str):
    line_bot_api.reply_message(
        line_event.reply_token,
        TextSendMessage(
            f"{command} 명령어는 존재하지 않습니다. 명령어 목록은 `!명령어` 입력을 통해 확인하실 수 있습니다."
        ),
    )
