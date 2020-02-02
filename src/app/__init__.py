import re

from linebot import WebhookHandler
from linebot.models import MessageEvent, TextMessage

from app.config import LINEBOT_SECRET, CELEBRATING_TARGET
from app.message import send_help_message, send_error_message
from app.message.leaderboard import celebrating_birthday, send_leaderboard
from app.message.vote import create_vote, answer_vote, close_vote

handler = WebhookHandler(LINEBOT_SECRET)


@handler.add(MessageEvent, message=TextMessage)
def message(line_event):
    if line_event.source.type != "group":
        return
    p1 = re.compile(CELEBRATING_TARGET)
    p2 = re.compile("생일")
    text = line_event.message.text
    p3 = re.compile(r"^!(\S+)(| .+)$")
    if p1.search(text) and p2.search(text):
        celebrating_birthday(line_event)
    elif p3.match(text):
        command = p3.match(text)[1]
        args = p3.match(text)[2].lstrip()
        if command in ["명령어"]:
            send_help_message(line_event, args)
        elif command in ["순위"]:
            send_leaderboard(line_event)
        elif command in ["투표시작"]:
            create_vote(line_event, args)
        elif command in ["투표"]:
            answer_vote(line_event, args)
        elif command in ["투표종료"]:
            close_vote(line_event)
        else:
            send_error_message(line_event, command)
    else:
        pass
