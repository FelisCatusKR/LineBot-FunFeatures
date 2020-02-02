from linebot.models import TextSendMessage, FlexSendMessage

from app.config import CELEBRATING_TARGET
from app.crud.leaderboard import update_amount, get_list_of_amount
from . import line_bot_api, exception_handler


@exception_handler
def celebrating_birthday(line_event):
    group_id = line_event.source.group_id
    user_id = line_event.source.user_id
    update_amount(group_id, user_id)
    line_bot_api.reply_message(line_event.reply_token, TextSendMessage("🎉"))


@exception_handler
def send_leaderboard(line_event):
    group_id = line_event.source.group_id
    line_bot_api.push_message(
        group_id, [TextSendMessage("집계중입니다...")], notification_disabled=True
    )
    response = get_list_of_amount(group_id)
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

    count = 1
    rank = 1
    last_amount = 0
    for item in response["Items"]:
        if int(item["amount"]) != last_amount:
            rank = count
            last_amount = int(item["amount"])
        user_id = item["user_id"]
        user_profile = line_bot_api.get_group_member_profile(group_id, user_id)
        user_name = user_profile.display_name
        leaderboard_item = {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {"type": "text", "text": f"{rank}위", "flex": 3, "weight": "bold"},
                {"type": "text", "text": user_name, "flex": 6, "weight": "bold"},
                {
                    "type": "text",
                    "text": str(item["amount"]),
                    "flex": 2,
                    "align": "end",
                    "gravity": "center",
                },
            ],
        }
        if rank is 1:
            leaderboard_item["contents"][0]["size"] = "xxl"
            leaderboard_item["contents"][0]["color"] = "#A4B60F"
            leaderboard_item["contents"][1]["size"] = "xxl"
        elif rank is 2:
            leaderboard_item["contents"][0]["size"] = "xl"
            leaderboard_item["contents"][0]["color"] = "#878787"
            leaderboard_item["contents"][1]["size"] = "xl"
        elif rank is 3:
            leaderboard_item["contents"][0]["size"] = "lg"
            leaderboard_item["contents"][0]["color"] = "#8A6200"
            leaderboard_item["contents"][1]["size"] = "lg"
        else:
            pass
        contents["body"]["contents"].append(leaderboard_item)
        count += 1

    line_bot_api.reply_message(
        line_event.reply_token,
        FlexSendMessage(alt_text="Leaderboard", contents=contents),
    )
