import base64
import gzip
import json
from io import StringIO

import boto3
import pandas as pd
from botocore.exceptions import ClientError

BUCKET_NAME = "fantasy-forecaster-data"
DYNAMODB_TABLE_NAME = "FantasyForecasterTable"

def write_s3(df, file_key):
    s3 = boto3.client('s3')
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    s3.put_object(Bucket=BUCKET_NAME, Key=file_key, Body=csv_buffer.getvalue())

def read_s3(file_key):
    s3 = boto3.client('s3')
    try:
        csv_obj = s3.get_object(Bucket=BUCKET_NAME, Key=file_key)
    except ClientError:
        return None
    body = csv_obj['Body']
    csv_string = body.read().decode('utf-8')
    df = pd.read_csv(StringIO(csv_string))
    return df

def read_s3_config(file_key='config.json'):
    s3 = boto3.client('s3')
    try:
        json_obj = s3.get_object(Bucket=BUCKET_NAME, Key=file_key)
    except ClientError:
        raise Exception('config file not found')
    
    body = json_obj['Body']
    json_string = body.read().decode('utf-8')
    config = json.loads(json_string)
    return config

def write_dynamo(id, data_dict):
    dynamodb = boto3.client('dynamodb')
    json_data = json.dumps(data_dict)
    compressed_data = gzip.compress(json_data.encode('utf-8'))
    base64_data = base64.b64encode(compressed_data).decode('utf-8')
    
    dynamodb.put_item(
        TableName=DYNAMODB_TABLE_NAME,
        Item={
            'id': {'S': id},
            'data': {'S': base64_data}
        }
    )
