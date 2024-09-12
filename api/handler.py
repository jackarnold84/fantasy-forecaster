import json
import time

from db import read_dynamo

CACHE_EXPIRATION = 600  # 10 minutes
cache = {}


def api_response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'application/json',
            'Access-Control-Allow-Methods': 'GET',
        },
        'body': json.dumps(body)
    }


def lambda_handler(event, _):
    query_params = event.get('queryStringParameters') or {}
    sport = query_params.get('sport', '')
    tag = query_params.get('tag', '')
    if not sport or not tag:
        return api_response(
            400,
            {'message': "error: query parameters 'sport' and 'tag' are required"},
        )
    id = f"{sport}-{tag}"

    # Check cache
    current_time = time.time()
    if id in cache:
        cached_data, timestamp = cache[id]
        if current_time - timestamp < CACHE_EXPIRATION:
            return api_response(
                200,
                {'data': cached_data},
            )
        else:
            del cache[id]

    # Query the database
    data = read_dynamo(id)
    if data is None:
        return api_response(
            404,
            {'message': f'error: data not found for {id}'},
        )
    cache[id] = (data, current_time)

    return api_response(
        200,
        {'data': data},
    )
