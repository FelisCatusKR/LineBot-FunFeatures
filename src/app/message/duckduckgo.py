from linebot.models import TextSendMessage, ImageSendMessage

from . import line_bot_api, exception_handler
from app.util.duckduckgo import duckduckgo_image_search


@exception_handler
def send_image_search_message(line_event, args: str):
    if args == "":
        line_bot_api.reply_message(
            line_event.reply_token, TextSendMessage("이미지 검색에 에러가 발생했습니다: 키워드가 없습니다."),
        )
    else:
        try:
            (image_link, thumb_link) = duckduckgo_image_search(args)
            line_bot_api.reply_message(
                line_event.reply_token, ImageSendMessage(image_link, thumb_link)
            )
        except:
            line_bot_api.reply_message(
                line_event.reply_token, TextSendMessage("이미지 처리 중 에러가 발생했습니다."),
            )
