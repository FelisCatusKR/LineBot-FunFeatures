import decimal

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

TABLE_NAME = "linebot-happybirthdayleaderboard-leaderdoards"
INDEX_NAME = "group_id-amount-index"

dynamodb = boto3.resource("dynamodb", region_name="ap-northeast-2")


def create_table():
    try:
        response = dynamodb.create_table(
            TableName=TABLE_NAME,
            KeySchema=[
                {"AttributeName": "group_id", "KeyType": "HASH"},
                {"AttributeName": "user_id", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "group_id", "AttributeType": "S"},
                {"AttributeName": "user_id", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "group_id-amount-index",
                    "KeySchema": [
                        {"AttributeName": "group_id", "KeyType": "HASH"},
                        {"AttributeName": "amount", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                }
            ],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
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


def update_amount(group_id: str, user_id: str):
    table = get_table()
    response = table.get_item(Key={"group_id": group_id, "user_id": user_id})
    if "Item" not in response:
        table.put_item(
            Item={
                "group_id": group_id,
                "user_id": user_id,
                "amount": decimal.Decimal(0),
            }
        )
    table.update_item(
        Key={"group_id": group_id, "user_id": user_id},
        UpdateExpression="set amount = amount + :val",
        ExpressionAttributeValues={":val": decimal.Decimal(1)},
        ReturnValues="UPDATED_NEW",
    )


def get_list_of_amount(group_id: str):
    table = get_table()
    return table.query(
        IndexName=INDEX_NAME,
        KeyConditionExpression=Key("group_id").eq(group_id),
        ScanIndexForward=False,
    )
