import decimal
import typing

from botocore.exceptions import ClientError

from . import dynamodb

TABLE_NAME = "linebot-funfeatures-votes"


class OngoingVoteError(Exception):
    pass


class OutOfRangeError(Exception):
    pass


class DuplicateItemError(Exception):
    pass


class InvalidUserError(Exception):
    pass


def get_table():
    try:
        response = dynamodb.create_table(
            TableName=TABLE_NAME,
            KeySchema=[{"AttributeName": "group_id", "KeyType": "HASH"},],
            AttributeDefinitions=[{"AttributeName": "group_id", "AttributeType": "S"},],
            ProvisionedThroughput={"ReadCapacityUnits": 1, "WriteCapacityUnits": 1},
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceInUseException":
            try:
                response = dynamodb.Table(TABLE_NAME)
            except ClientError:
                raise
            else:
                return response
        else:
            raise
    else:
        return response


def create_vote(group_id: str, user_id: str, title: str, items: typing.List[str]):
    table = get_table()
    response = table.get_item(Key={"group_id": group_id})
    if "Item" not in response:
        table.put_item(Item={"group_id": group_id, "ongoing": False, "votes": []})
        response = table.get_item(Key={"group_id": group_id})
    if response["Item"]["ongoing"] is True:
        raise OngoingVoteError
    try:
        table.update_item(
            Key={"group_id": group_id},
            UpdateExpression="SET ongoing = :val, votes = list_append(votes, :vote)",
            ExpressionAttributeValues={
                ":val": True,
                ":vote": [
                    {
                        "user_id": user_id,
                        "title": title,
                        "item_list": items,
                        "results": [decimal.Decimal(0)] * len(items),
                        "answers": {},
                    }
                ],
            },
        )
    except ClientError:
        raise
    try:
        response = table.get_item(Key={"group_id": group_id})
    except ClientError:
        raise
    else:
        return response


def read_vote(group_id: str):
    table = get_table()
    response = table.get_item(Key={"group_id": group_id})
    if "Item" not in response:
        table.put_item(Item={"group_id": group_id, "ongoing": False, "votes": []})
        response = table.get_item(Key={"group_id": group_id})
    if len(response["Item"]["votes"]) == 0:
        raise OngoingVoteError
    else:
        return response


def close_vote(group_id: str, user_id: str):
    table = get_table()
    response = table.get_item(Key={"group_id": group_id})
    if "Item" not in response or response["Item"]["ongoing"] is False:
        raise OngoingVoteError
    vote_idx = len(response["Item"]["votes"]) - 1
    if response["Item"]["votes"][vote_idx]["user_id"] != user_id:
        raise InvalidUserError
    try:
        table.update_item(
            Key={"group_id": group_id},
            UpdateExpression="SET ongoing = :val",
            ExpressionAttributeValues={":val": False},
        )
    except ClientError:
        raise
    try:
        response = table.get_item(Key={"group_id": group_id})
    except ClientError:
        raise
    else:
        return response


def answer_vote(group_id: str, user_id: str, answer: int):
    table = get_table()
    response = table.get_item(Key={"group_id": group_id})
    if "Item" not in response or response["Item"]["ongoing"] is False:
        raise OngoingVoteError
    vote_idx = len(response["Item"]["votes"]) - 1
    if answer < 0 or answer >= len(response["Item"]["votes"][vote_idx]["item_list"]):
        raise OutOfRangeError
    if user_id not in response["Item"]["votes"][vote_idx]["answers"]:
        try:
            table.update_item(
                Key={"group_id": group_id},
                UpdateExpression=f"SET votes[{vote_idx}].answers.{user_id} = :val1, votes[{vote_idx}].results[{answer}] = votes[{vote_idx}].results[{answer}] + :val2",
                ExpressionAttributeValues={
                    ":val1": decimal.Decimal(answer),
                    ":val2": decimal.Decimal(1),
                },
            )
        except ClientError:
            raise
    else:
        prev_answer = response["Item"]["votes"][vote_idx]["answers"][user_id]
        if prev_answer == answer:
            pass
        else:
            try:
                table.update_item(
                    Key={"group_id": group_id},
                    UpdateExpression=f"SET votes[{vote_idx}].answers.{user_id} = :val1, votes[{vote_idx}].results[{prev_answer}] = votes[{vote_idx}].results[{prev_answer}] - :val2, votes[{vote_idx}].results[{answer}] = votes[{vote_idx}].results[{answer}] + :val2",
                    ExpressionAttributeValues={
                        ":val1": decimal.Decimal(answer),
                        ":val2": decimal.Decimal(1),
                    },
                )
            except ClientError:
                raise
    try:
        response = table.get_item(Key={"group_id": group_id})
    except ClientError:
        raise
    else:
        return response


def add_item(group_id: str, user_id: str, item: str):
    table = get_table()
    response = table.get_item(Key={"group_id": group_id})
    if "Item" not in response or response["Item"]["ongoing"] is False:
        raise OngoingVoteError
    vote_idx = len(response["Item"]["votes"]) - 1
    if item in response["Item"]["votes"][vote_idx]["item_list"]:
        raise DuplicateItemError
    try:
        table.update_item(
            Key={"group_id": group_id},
            UpdateExpression=f"SET votes[{vote_idx}].item_list = list_append(votes[{vote_idx}].item_list, :val1), votes[{vote_idx}].results = list_append(votes[{vote_idx}].results, :val2)",
            ExpressionAttributeValues={":val1": [item], ":val2": [decimal.Decimal(0)]},
        )
    except ClientError:
        raise
    item_idx = len(response["Item"]["votes"][vote_idx]["item_list"])
    try:
        response = answer_vote(group_id, user_id, item_idx)
    except ClientError:
        raise
    else:
        return response
