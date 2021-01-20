import json
import boto3
import requests
from aws_requests_auth.aws_auth import AWSRequestsAuth
from requests_aws4auth import AWS4Auth
from elasticsearch import Elasticsearch, client, RequestsHttpConnection

BUCKET_NAME = "hw3-fall2020-photos"

def get_imgname(event):
    try:
        return event['Records'][0]['s3']['object']['key']
    except IndexError as e:
        raise e
        
# https://docs.aws.amazon.com/rekognition/latest/dg/labels-detect-labels-image.html
def get_labels(imgname):
    rekognition = boto3.client('rekognition')
    resp = rekognition.detect_labels(Image={'S3Object':{'Bucket':BUCKET_NAME,
    'Name':imgname}}, MaxLabels=10)
    if not resp or not resp["Labels"]: print('### ERROR: NO LABEL FOUND ', resp)
    else: 
        # detected object with bounds (dog, person, car, etc)
        concrete = [l['Name'] for l in resp["Labels"] if l['Instances']]
        # abstract class and background misc (mammal, vehicle, grass, etc)
        abstract = [l['Name'] for l in resp["Labels"] if not l['Instances']]
        return concrete+abstract
        # return {'concrete': concrete, 'abstract': abstract, 'all': concrete+abstract}

def lambda_handler(event, context):
    host = 'search-hw3-search-dl7wdgujatvmsve3akfrrxpqqq.us-east-1.es.amazonaws.com'
    region = 'us-east-1'
    service = 'es'
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
    es = Elasticsearch(
        hosts=[{'host':host, 'port':443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection)
    createindexbody = {
          "settings": {
            "number_of_shards": 1
          }
        }
    indc = es.indices
    CreatedNewIndex = False
    if not es.indices.exists(index="searchphotos"):
        indc.create('searchphotos', body=createindexbody)
        CreatedNewIndex = True
    indc.open('searchphotos')
    
    for record in event['Records']:
        imgname = get_imgname(event)
        print(imgname)
        labels=get_labels(imgname)
        print(labels)
        query={'objectKey':imgname,'bucket':BUCKET_NAME,'labels':labels}
        data = json.dumps(query)
        response = es.index('searchphotos', data, id=imgname)
        print ("resp",response)
    
    
    # """
    # print("### EVENT: ", event)
    # imgname = get_imgname(event)
    # print("### IMG_NAME: ", imgname)
    # labels = get_labels(imgname)
    # print("### LABELS: ", labels)
    #  print(event)
    # """
    # # let's talk to our AWS Elasticsearch cluster
    # auth = AWSRequestsAuth(aws_access_key='',
    #                   aws_secret_access_key='',
    #                   aws_host='search-search-photos.us-east-1.es.amazonaws.com',
    #                   aws_region='us-east-1',
    #                   aws_service='es')

    # response = requests.get('http://search-search-photos-sjulua7wdvh7kntpt4yvcmxxkq.us-east-1.es.amazonaws.com',
    #                     auth=auth)
    # print("response",response.content)
    
    # for record in event['Records']:
    #     imgname = get_imgname(event)
    #     print(imgname)
    #     labels=get_labels(imgname)
    #     print(labels)
    #     URL = "https://search-search-photos-sjulua7wdvh7kntpt4yvcmxxkq.us-east-1.es.amazonaws.com/photos/_doc"
    #     header={"Content-Type":"application/json"}
    #     query={'objectKey':imgname,'bucket':BUCKET_NAME,'labels':labels}
    #     data = json.dumps(query)
    #     print("data",data)
    #     response = requests.post(URL,data,headers = header)
    #     #dat=json.loads(response.text)
    #     print ("dat",response)
       
   
    
    return {
        'statusCode': 200,
        'body': json.dumps('OK')
    }
