import json
import os
import uuid
import logging

import boto3

LOG = logging.getLogger()
LOG.setLevel(logging.INFO)

# watch for spelling errors guy; cmon!

def main(event, context):
    LOG.info("EVENT: " + json.dumps(event))

    query_string_params = event['queryStringParameters']
    if query_string_params is not None:
        target_url = query_string_params['targetUrl']
        if target_url is not None:
            return create_short_url(event)

    path_parameters = event['pathParameters']
    if path_parameters is not None:
        if path_parameters['proxy'] is not None:
            return read_short_url(event)

    return {
        'statusCode': 200,
        'body': 'usage: ?targetUrl=URL'
    }


def create_short_url(event):
    # pull out dynamodb table name from env
    table_name = os.environ.get('TABLE_NAME')

    # parse targetUrl
    target_url = event["queryStringParameters"]['targetUrl']

    # create unique id (take first 8 characters)
    id = str(uuid.uuid4())[0:8]

    # create item in dynamodb table
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    table.put_item(Item={
        'id': id,
        'target_url': target_url
    })

    #create redirect url
    url = "https://" \
        + event["requestContext"]["domainName"] \
        + event["requestContext"]["path"] \
        + id

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/plain'},
        'body': 'Created URL: %s' % url
    }


def read_short_url(event):
    # parse redirect id from path
    id = event['pathParameters']['proxy']

    # pull out Dynamodb table name from environment
    table_name = os.environ.get('TABLE_NAME')

    # load redirect target from Dynamodb
    ddb = boto3.resource('dynamodb')
    table = ddb.Table(table_name)
    response = table.get_item(Key={'id': id})
    LOG.debug("Response: " + json.dumps(response))

    item = response.get("Item", None)
    if item is None:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'text/plain'},
            'body': 'No redirect found for ' + id
        }

# Respond with a redirect - return 301 code to client and redirect
    return {
        'statusCode': 301,
        'headers': {
            'Location': item.get('target_url')
            }
    }