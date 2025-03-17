import json
import boto3
import botocore
from datetime import datetime
import base64

def lambda_handler(event, context):
    
    event = json.loads(event['body'])
    message = event['message']

    bedrock = boto3.client(
        "bedrock-runtime", region_name="us-west-2", config=botocore.config.Config(read_timeout=300, retries={'max_attempts': 3})
    )
    s3 = boto3.client('s3')
    payload = {
        "prompt": message,
        "mode": "text-to-image",
        "aspect_ratio": "1:1",
        "output_format": "jpeg",
        "seed": 0,
    }
    

    response = bedrock.invoke_model(
        body=json.dumps(payload),
        modelId="stability.stable-image-core-v1:0",
        accept="application/json",
        contentType="application/json",
    )

    response_body = json.loads(response.get("body").read())
    base_64_img_str = response_body["images"][0]
    image_content = base64.b64decode(base_64_img_str)

    bucket_name = 'bedrock-course-bucket-01'
    current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    s3_key = f"output-images/{current_time}.jpg"

    s3.put_object(Bucket=bucket_name, Key=s3_key, Body=image_content, ContentType='image/jpg')

    return {
        'statusCode': 200,
        'body': json.dumps('Image saved to s3')
    }
