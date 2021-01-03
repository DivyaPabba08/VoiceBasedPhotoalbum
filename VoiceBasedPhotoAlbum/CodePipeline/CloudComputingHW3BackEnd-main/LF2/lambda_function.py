import json
import math
import dateutil.parser
import datetime
import time
import os
import logging
import boto3
import json
from requests_aws4auth import AWS4Auth
from elasticsearch import Elasticsearch, client, RequestsHttpConnection

def initialize_elastic():
    host = 'search-hw3-search-dl7wdgujatvmsve3akfrrxpqqq.us-east-1.es.amazonaws.com'
    region = 'us-east-1'
    service = 'es'
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
    es = Elasticsearch(hosts=[{'host':host, 'port':443}],
                       http_auth=awsauth,
                       use_ssl=True,
                       verify_certs=True,
                       connection_class=RequestsHttpConnection)
    return es

def searchPhotos(keywords):
    res = []
    es = initialize_elastic()
    for kw in keywords:
        response = es.search(index="searchphotos",
             body={
                "query": {
                    "match": {
                        "labels": kw
                    }
                }
             }
        )
        print('#############', response)
        hits = response['hits']['hits']
        if not hits:
            print('######### No match found for ', kw)
            continue
        newphotos = [h['_id'] for h in hits if h['_id'] not in res]
        if newphotos: res.append(newphotos[0])
        else: res.append(hits[0]['_id'])
    res = ["https://hw3-fall2020-photos.s3.amazonaws.com/" + p for p in res]
    # res.append("https://hw3-fall2020-photos.s3.amazonaws.com/dog.jpg")
    # res.append("https://hw3-fall2020-photos.s3.amazonaws.com/ice.jpg")
    return res

def get_slots(lex_response):
    slots_dict = lex_response['slots']
    results = []
    for key in slots_dict.keys():
        result = slots_dict[key]
        if result:
            results.append(result)
    return results

def sendToLex(message):
    client = boto3.client('lex-runtime')
    response = client.post_text(
        botName="SearchBot",
        botAlias="SearchAlias",
        userId='176748515449',
        inputText= message)
    return response
    
def lambda_handler(event, context):
    message = event["queryStringParameters"]["q"]
    # message = event['message']
    print(message)
    response = sendToLex(message)
    # return(json.dumps(response))
    intent_name = response['intentName']
    categories = None
    if intent_name == 'SearchIntent':
        categories = get_slots(response)
        print(categories) #[cats, dogs]
    else:
        print('Intent with name ' + intent_name + ' not supported')
    photos = []
    if categories: photos = searchPhotos(categories)
    return {
        'headers': {
            "Access-Control-Allow-Headers" : "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,GET,POST"
        },
        'statusCode': 200,
        'body': json.dumps(photos)
    }