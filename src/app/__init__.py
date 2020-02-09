import re

from linebot import WebhookHandler
from linebot.models import MessageEvent, TextMessage

from app.config import LINEBOT_SECRET, CELEBRATING_TARGET
from app.message import send_help_message, send_error_message
from app.message import leaderboard, vote, duckduckgo, etc

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
        leaderboard.celebrating_birthday(line_event)
    elif p3.match(text):
        command = p3.match(text)[1]
        args = p3.match(text)[2].lstrip()
        if command in ["명령어"]:
            send_help_message(line_event, args)
        elif command in ["순위"]:
            leaderboard.send_leaderboard(line_event)
        elif command in ["투표시작"]:
            vote.create_vote(line_event, args)
        elif command in ["투표"]:
            vote.answer_vote(line_event, args)
        elif command in ["투표항목"]:
            vote.add_item(line_event, args)
        elif command in ["투표종료"]:
            vote.close_vote(line_event)
        elif command in ["선택장애"]:
            etc.select_random_item(line_event, args)
        elif command in ["이미지"]:
            duckduckgo.send_image_search_message(line_event, args)
        else:
            send_error_message(line_event, command)
    else:
        pass
