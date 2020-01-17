from linebot import LineBotApi
from linebot.models import TextSendMessage

from .config import LINEBOT_ACCESS_TOKEN
from .database import update_amount, get_list_of_amount

line_bot_api = LineBotApi(LINEBOT_ACCESS_TOKEN)


def celebrating_birthday(line_event):
    if line_event.source.type == "group":
        group_id = line_event.source.group_id
    else:
        group_id = "test"
    user_id = line_event.source.user_id
    update_amount(group_id, user_id)
    line_bot_api.reply_message(line_event.reply_token, TextSendMessage("🎉"))


def leaderboard(line_event):
    line_bot_api.reply_message(line_event.reply_token, TextSendMessage("준비중입니다"))
