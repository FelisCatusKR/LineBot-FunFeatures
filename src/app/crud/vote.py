from typing import List

from botocore.exceptions import ClientError

from . import dynamodb

TABLE_NAME = "linebot-funfeatures-votes"


class OngoingVoteError(Exception):
    pass


class OutOfRangeError(Exception):
    pass


class InvalidUserError(Exception):
    pass


def create_table():
    try:
        response = dynamodb.create_table(
            TableName=TABLE_NAME,
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"},],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"},],
            ProvisionedThroughput={"ReadCapacityUnits": 1, "WriteCapacityUnits": 1},
        )
    except ClientError:
        raise
    else:
        return response


def get_table():
    try:
        response = dynamodb.Table(TABLE_NAME)
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            response = create_table()
        else:
            raise
    return response


def create_vote(user_id: str, title: str, items: List[str]):
    table = get_table()
    item_count = table.item_count
    if item_count > 0:
        response = table.get_item(Key={"id": "vote-" + str(item_count + 1).zfill(6)})
        if response["Item"]["ongoing"] is True:
            raise OngoingVoteError
    table.put_item(
        Item={
            "id": "vote-" + str(item_count + 1).zfill(6),
            "user_id": user_id,
            "title": title,
            "items": items,
            "ongoing": True,
        }
    )


def close_vote(user_id: str):
    table = get_table()
    item_count = table.item_count
    if item_count == 0:
        raise OutOfRangeError
    response = table.get_item(Key={"id": "vote-" + str(item_count).zfill(6)})
    if response["Item"]["ongoing"] is False:
        raise OngoingVoteError
    if response["Item"]["user_id"] != user_id:
        raise InvalidUserError
    table.update_item(
        Key={"id": "vote-" + str(item_count).zfill(6)},
        UpdateExpression="SET ongoing = :val",
        ExpressionAttributeValues={":val": False},
    )


def answer_vote(user_id: str, answer: int):
    table = get_table()
    item_count = table.item_count
    if item_count == 0:
        raise OutOfRangeError
    response = table.get_item(Key={"id": "vote-" + str(item_count).zfill(6)})
    if response["Item"]["ongoing"] is False:
        raise OngoingVoteError
    if user_id not in response["Item"]["answers"]:
        pass
    table.update_item(
        Key={"id": "vote-" + str(item_count).zfill(6)},
        UpdateExpression="SET answers = list_append(answers, :val)",
        ExpressionAttributeValues={":val": [answer]},
    )


def get_vote():
    table = get_table()
    item_count = table.item_count
    if item_count == 0:
        raise OutOfRangeError
    response = table.get_item(Key={"id": "vote-" + str(item_count).zfill(6)})
    return response
