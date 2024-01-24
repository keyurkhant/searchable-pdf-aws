import json
import boto3
import requests
import os

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    # Textract JSON file bucket and document
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    document_name = event['Records'][0]['s3']['object']['key']
    res_name = document_name.replace('response' , 'output').replace('json', 'pdf')
    # Json Document key
    json_document = event['Records'][0]['s3']['object']['key']
    input_document = res_name.replace('output', 'input')
    s3_client.download_file(bucket_name, json_document, '/tmp/response.json')
    
    s3_client.download_file(os.environ.get('INPUT_BUCKET_NAME'), input_document, '/tmp/input.pdf')
    
    # url = 'http://ec2-54-82-53-74.compute-1.amazonaws.com:5002/pdf-process'
    url = os.environ.get('EC2_URL') + 'pdf-process'
    
    files = {
        'pdf': ('input.pdf', open('/tmp/input.pdf', 'rb'), 'application/pdf'),
        'json': ('response.json', open('/tmp/response.json', 'rb'), 'application/json')
    }

    try:
        response = requests.post(url, files=files)
        
    except Exception as e:
        print("Error : ",e)

    if response.status_code == 200:
        with open('/tmp/output.pdf', 'wb') as f:
            f.write(response.content)
        s3_client.upload_file('/tmp/output.pdf', os.environ.get('OUTPUT_BUCKET_NAME'),res_name)
        print("SUCCESS")
        return {
            'statusCode': 200,
            'body': json.dumps('Output stored successfully!')
        }
    else:
        print("FAILURE")
        return {
            'statusCode': 500,
            'body': json.dumps('Output failed to process!')
        }