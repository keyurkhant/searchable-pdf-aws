import json
import boto3
import time
import os

textract = boto3.client('textract')
s3 = boto3.client('s3')

def lambda_handler(event, context):
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    document_name = event['Records'][0]['s3']['object']['key']

    output_bucket = os.environ.get('JSON_BUCKET_NAME')
    res_name = document_name.replace('input' , 'response').replace('pdf', 'json')
    
    print(bucket_name)
    print(document_name)
    
    try:
        textract_response = textract.analyze_document(
            Document = {
                'S3Object': {
                    'Bucket': bucket_name,
                    'Name': document_name
                }
            },
            FeatureTypes=['TABLES', 'FORMS']
        )
        
        print("Textract Response: ", textract_response)
        textract_response_json = json.dumps(textract_response)
        s3.put_object(Body=textract_response_json, Bucket=output_bucket, Key=res_name)

    except Exception as err:
        print('Error::textract failed:: ', err)
    
    return {
        'statusCode': 200,
        'body': json.dumps(textract_response)
    }
