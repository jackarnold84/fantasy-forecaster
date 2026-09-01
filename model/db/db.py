import base64
import gzip
import json
import os
from io import StringIO

import boto3
import pandas as pd
from botocore.exceptions import ClientError

BUCKET_NAME = "fantasy-forecaster-data"
DYNAMODB_TABLE_NAME = "FantasyForecasterTable"

READ_MOCK = os.environ.get('DB_READ', '').lower() != 'prod'
WRITE_MOCK = os.environ.get('DB_WRITE', '').lower() != 'prod'
MOCK_DB_ROOT = os.environ.get('MOCK_DB_ROOT', '.mock-db')


def write_s3(df, file_key):
    if WRITE_MOCK:
        file_path = os.path.join(MOCK_DB_ROOT, file_key)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        df.to_csv(file_path, index=False)
        print('--> written to mock bucket:', file_key)
    else:
        s3 = boto3.client('s3')
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)
        s3.put_object(Bucket=BUCKET_NAME, Key=file_key,
                      Body=csv_buffer.getvalue())
        print('--> written to s3 bucket:', file_key)


def read_s3(file_key):
    if READ_MOCK:
        print('--> reading from mock bucket:', file_key)
        return pd.read_csv(os.path.join(MOCK_DB_ROOT, file_key))
    else:
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
    if READ_MOCK:
        print('--> reading from mock bucket:', file_key)
        with open(os.path.join(MOCK_DB_ROOT, file_key), 'r') as f:
            config = json.load(f)
        return config
    else:
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
    if WRITE_MOCK:
        table_dir = os.path.join(MOCK_DB_ROOT, 'table')
        os.makedirs(table_dir, exist_ok=True)
        with open(os.path.join(table_dir, f'{id}.json'), 'w') as f:
            json.dump(data_dict, f)
        print('--> written to mock db:', id)
    else:
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
        print('--> written to dynamo db:', id)
