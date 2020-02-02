from linebot.models import TextSendMessage, FlexSendMessage

from app.crud.vote import create_vote, answer_vote, close_vote, get_vote
from . import line_bot_api, exception_handler


@exception_handler
def create_vote(line_event, args: str):
    line_bot_api.reply_message(
        line_event.reply_token, TextSendMessage("준비중입니다."),
    )


@exception_handler
def answer_vote(line_event, args: str):
    line_bot_api.reply_message(
        line_event.reply_token, TextSendMessage("준비중입니다."),
    )


@exception_handler
def close_vote(line_event, args: str):
    line_bot_api.reply_message(
        line_event.reply_token, TextSendMessage("준비중입니다."),
    )
