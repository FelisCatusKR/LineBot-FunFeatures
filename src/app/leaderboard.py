from linebot import LineBotApi
from linebot.models import TextSendMessage, FlexSendMessage

from .config import LINEBOT_ACCESS_TOKEN, CELEBRATING_TARGET
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


def send_leaderboard(line_event):
    if line_event.source.type != "group":
        return
    group_id = line_event.source.group_id
    response = get_list_of_amount(group_id)
    count = 1
    contents = {
        "type": "bubble",
        "styles": {"header": {"backgroundColor": "#E3D3A3"}},
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "생일 축하 리더보드",
                    "size": "xl",
                    "align": "center",
                    "weight": "bold",
                }
            ],
        },
        "body": {"type": "box", "layout": "vertical", "spacing": "md", "contents": []},
        "footer": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "button",
                    "action": {
                        "type": "message",
                        "label": "생일 축하하기",
                        "text": f"{CELEBRATING_TARGET}아 생일 축하해!",
                    },
                    "style": "primary",
                }
            ],
        },
    }

    for item in response["Items"]:
        leaderboard_item = {"type": "box", "layout": "horizontal", "contents": None}
        user_id = item["user_id"]
        user_profile = line_bot_api.get_profile(user_id)
        user_name = user_profile.display_name
        columns = [None, None, None]
        columns[0] = {
            "type": "text",
            "text": f"{count}위",
            "flex": 3,
            "weight": "bold",
        }
        columns[1] = {
            "type": "text",
            "text": user_name,
            "flex": 6,
            "weight": "bold",
        }
        columns[2] = {
            "type": "text",
            "text": str(item["amount"]),
            "flex": 2,
            "align": "end",
            "gravity": "center",
        }
        if count is 1:
            columns[0]["size"] = "xxl"
            columns[0]["color"] = "#A4B60F"
            columns[1]["size"] = "xxl"
        elif count is 2:
            columns[0]["size"] = "xl"
            columns[0]["color"] = "#878787"
            columns[1]["size"] = "xl"
        elif count is 3:
            columns[0]["size"] = "lg"
            columns[0]["color"] = "#8A6200"
            columns[1]["size"] = "lg"
        else:
            pass
        leaderboard_item["contents"] = columns
        contents["body"]["contents"].append(leaderboard_item)
        count += 1
    line_bot_api.reply_message(
        line_event.reply_token,
        FlexSendMessage(alt_text="Leaderboard", contents=contents),
    )
