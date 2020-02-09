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
        line_event.reply_token,
        TextSendMessage(
            """`!순위` 생일 축하 횟수의 순위표를 출력합니다.
`!투표시작 투표_제목|항목_1|항목_2(|항목_3|...)` 투표를 시작합니다. 현재 진행중인 다른 투표가 없을 때만 가능합니다.
`!투표` 가장 최근에 게시된 투표를 불러옵니다.
`!투표 항목_번호` 투표의 특정 항목으로 응답합니다. 현재 진행중인 투표가 있을 경우에만 사용 가능합니다.
`!투표항목 새로운_항목` 투표에 새로운 항목을 추가합니다. 현재 진행중인 투표가 있을 경우에만 가능합니다.
`!투표종료` 진행중인 투표를 종료하고 결과를 출력합니다. 현재 진행중인 투표가 있는 상태에서 투표를 시작한 유저만 사용할 수 있습니다.
`!선택장애 항목_1|항목_2(|항목_3|...)` 무작위 항목을 선택해 메시지로 알려줍니다.
`!이미지 키워드` 해당 키워드로 DuckDuckGo 이미지 검색을 한 후, 최상위 이미지를 전송합니다."""
        ),
    )


@exception_handler
def send_error_message(line_event, command: str):
    line_bot_api.reply_message(
        line_event.reply_token,
        TextSendMessage(
            f"{command} 명령어는 존재하지 않습니다. 명령어 목록은 `!명령어` 입력을 통해 확인하실 수 있습니다."
        ),
    )
