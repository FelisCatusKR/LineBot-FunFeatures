from linebot.models import TextSendMessage, FlexSendMessage

from app.crud import vote as crud_vote
from . import line_bot_api, exception_handler


def create_vote_message(response: dict):
    vote = response["Item"]["votes"][-1]
    is_ongoing = response["Item"]["ongoing"]
    contents = {
        "type": "bubble",
        "size": "giga",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "size": "xs"},
                {
                    "type": "text",
                    "text": vote["title"],
                    "size": "lg",
                    "weight": "bold",
                    "wrap": True,
                },
            ],
        },
        "body": {
            "type": "box",
            "layout": "horizontal",
            "spacing": "md",
            "contents": [
                {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "flex": 1,
                    "contents": [],
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "flex": 3,
                    "contents": [],
                },
            ],
        },
        "styles": {"body": {"separator": True}},
    }
    for idx in range(len(vote["item_list"])):
        contents["body"]["contents"][0]["contents"].append(
            {
                "type": "box",
                "layout": "horizontal",
                "paddingAll": "5px",
                "contents": [
                    {
                        "type": "text",
                        "text": vote["item_list"][idx],
                        "size": "sm",
                        "weight": "bold",
                    }
                ],
            }
        )
        content = {
            "type": "box",
            "layout": "horizontal",
            "backgroundColor": "#DFE4EAFF",
            "contents": [
                {
                    "type": "box",
                    "layout": "baseline",
                    "contents": [{"type": "text", "text": " "}],
                },
                {
                    "type": "box",
                    "layout": "baseline",
                    "paddingAll": "5px",
                    "contents": [
                        {
                            "type": "text",
                            "text": str(vote["results"][idx]),
                            "size": "sm",
                            "align": "end",
                        }
                    ],
                },
            ],
        }
        if is_ongoing:
            content["action"] = {
                "type": "message",
                "label": vote["item_list"][idx],
                "text": f"!투표 {idx + 1}",
            }
        if int(vote["results"][idx]) == 0:
            pass
        elif int(vote["results"][idx]) == len(vote["answers"]):
            content["backgroundColor"] = "#00B900FF"
        else:
            content["contents"][0]["backgroundColor"] = "#00B900FF"
            content["contents"][0]["flex"] = int(vote["results"][idx])
            content["contents"][1]["flex"] = len(vote["answers"]) - int(
                vote["results"][idx]
            )
        contents["body"]["contents"][1]["contents"].append(content)
    if is_ongoing:
        contents["header"]["contents"][0]["text"] = "투표 현황"
        alt_text = "Vote Status"
    else:
        contents["header"]["contents"][0]["text"] = "투표 결과"
        alt_text = "Vote Result"
    return FlexSendMessage(alt_text=alt_text, contents=contents)


@exception_handler
def create_vote(line_event, args: str):
    arg_list = args.split("|")
    if len(arg_list) >= 3:
        try:
            response = crud_vote.create_vote(
                line_event.source.group_id,
                line_event.source.user_id,
                arg_list[0],
                arg_list[1:],
            )
        except crud_vote.OngoingVoteError:
            line_bot_api.reply_message(
                line_event.reply_token,
                TextSendMessage("투표 생성에 오류가 발생했습니다: 이미 진행중인 투표가 존재합니다."),
            )
        else:
            vote = response["Item"]["votes"][-1]
            contents = {
                "type": "bubble",
                "header": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {"type": "text", "text": "투표", "size": "xs"},
                        {
                            "type": "text",
                            "text": vote["title"],
                            "size": "lg",
                            "weight": "bold",
                            "wrap": True,
                        },
                    ],
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [],
                },
                "styles": {"body": {"separator": True}},
            }
            for idx, item in enumerate(vote["item_list"]):
                contents["body"]["contents"].append(
                    {
                        "type": "button",
                        "action": {
                            "type": "message",
                            "label": item,
                            "text": f"!투표 {idx + 1}",
                        },
                        "style": "primary",
                    }
                )
            line_bot_api.reply_message(
                line_event.reply_token,
                FlexSendMessage(alt_text="Vote", contents=contents),
            )
    else:
        line_bot_api.reply_message(
            line_event.reply_token,
            TextSendMessage(
                "투표 생성에 오류가 발생했습니다: 투표를 진행하기 위해서는 투표명과 최소한 두 개 이상의 투표항목을 포함해야 합니다."
            ),
        )


@exception_handler
def answer_vote(line_event, args: str):
    try:
        num = int(args)
    except ValueError:
        if args == "":
            try:
                response = crud_vote.read_vote(line_event.source.group_id)
            except crud_vote.OngoingVoteError:
                line_bot_api.reply_message(
                    line_event.reply_token,
                    TextSendMessage("투표 현황을 가져오는 도중 오류가 발생했습니다: 투표 내역이 없습니다."),
                )
            else:
                line_bot_api.reply_message(
                    line_event.reply_token, create_vote_message(response)
                )
        else:
            line_bot_api.reply_message(
                line_event.reply_token,
                TextSendMessage("투표 응답에 오류가 발생했습니다: 투표 응답은 숫자로만 가능합니다."),
            )
    else:
        try:
            crud_vote.answer_vote(
                line_event.source.group_id, line_event.source.user_id, num - 1
            )
        except crud_vote.OngoingVoteError:
            line_bot_api.reply_message(
                line_event.reply_token,
                TextSendMessage("투표 응답에 오류가 발생했습니다: 진행중인 투표가 없습니다."),
            )
        except crud_vote.OutOfRangeError:
            line_bot_api.reply_message(
                line_event.reply_token,
                TextSendMessage("투표 응답에 오류가 발생했습니다: 투표 항목을 초과한 숫자로 투표하셨습니다."),
            )


@exception_handler
def add_item(line_event, args: str):
    if args == "":
        line_bot_api.reply_message(
            line_event.reply_token,
            TextSendMessage("투표 항목 추가에 오류가 발생했습니다: 항목이 비어있습니다."),
        )
    else:
        try:
            response = crud_vote.read_vote(line_event.source.group_id)
        except crud_vote.OngoingVoteError:
            line_bot_api.reply_message(
                line_event.reply_token,
                TextSendMessage("투표 항목 추가에 오류가 발생했습니다: 진행중인 투표가 없습니다."),
            )
        else:
            if response["Item"]["ongoing"] is not True:
                line_bot_api.reply_message(
                    line_event.reply_token,
                    TextSendMessage("투표 항목 추가에 오류가 발생했습니다: 진행중인 투표가 없습니다."),
                )
            else:
                item = args.strip()
                try:
                    response = crud_vote.add_item(
                        line_event.source.group_id, line_event.source.user_id, item
                    )
                except crud_vote.DuplicateItemError:
                    line_bot_api.reply_message(
                        line_event.reply_token,
                        TextSendMessage("투표 항목 추가에 오류가 발생했습니다: 이미 존재하는 항목입니다."),
                    )
                else:
                    line_bot_api.reply_message(
                        line_event.reply_token, create_vote_message(response),
                    )


@exception_handler
def close_vote(line_event):
    try:
        response = crud_vote.close_vote(
            line_event.source.group_id, line_event.source.user_id
        )
    except crud_vote.InvalidUserError:
        line_bot_api.reply_message(
            line_event.reply_token,
            TextSendMessage("투표 종료에 오류가 발생했습니다: 투표를 게시한 유저만 투표를 종료할 수 있습니다."),
        )
    except crud_vote.OngoingVoteError:
        line_bot_api.reply_message(
            line_event.reply_token,
            TextSendMessage("투표 종료에 오류가 발생했습니다: 진행중인 투표가 없습니다."),
        )
    else:
        line_bot_api.reply_message(
            line_event.reply_token, create_vote_message(response),
        )
