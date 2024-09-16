import base64
import gzip
import json

import boto3

DYNAMODB_TABLE_NAME = "FantasyForecasterTable"

def read_dynamo(id):
    dynamodb = boto3.client('dynamodb')
    response = dynamodb.get_item(
        TableName=DYNAMODB_TABLE_NAME,
        Key={
            'id': {'S': id}
        }
    )
    if 'Item' not in response:
        return None
    
    base64_data = response['Item']['data']['S']
    compressed_data = base64.b64decode(base64_data)
    json_data = gzip.decompress(compressed_data).decode('utf-8')
    data_dict = json.loads(json_data)
    
    return data_dict
