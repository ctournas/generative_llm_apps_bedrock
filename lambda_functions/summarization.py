import boto3
import botocore.config
import json
import base64
from datetime import datetime
from email import message_from_bytes

def extract_text_from_multipart_(data):
    msg = message_from_bytes(data)

    text_content = ""

    if msg.is_multipart():
        for part in msg.walk():

            if part.get_content_type() == "text/plain":
                text_content += part.get_payload(decode=True).decode('utf-8') + '\n'

    else:
        if msg.get_content_type() == "text/plain":
            text_content = msg.get_payload(decode=True).decode('utf-8')

    return text_content.strip() if text_content else None

def generate_summary_from_bedrock(content:str) -> str:
    # Messages API format
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 2048,
        "temperature": 0.1,
        "top_k": 250,
        "top_p": 0.2,
        "messages": [
            {
                "role": "user",
                "content": f"Please provide a summary of the following meeting transcript. The summary should be in bullet points. The meeting transcript is as follows: {content}"
            }
        ]
    }
    
    try:
        bedrock = boto3.client('bedrock-runtime',
                               region_name='us-west-2',
                               config=botocore.config.Config(
                                                            read_timeout=300, 
                                                            retries={'max_attempts': 3})) 
        response = bedrock.invoke_model(
            body=json.dumps(request_body),
            modelId="anthropic.claude-3-5-sonnet-20241022-v2:0"
        )
        response_content = response.get("body").read().decode("utf-8")
        response_data = json.loads(response_content)

        # Extract the code from the response
        summary = response_data["content"][0]["text"]
        return summary
    
    except Exception as e:
        print(f"Error generating summary: {e}")
        return None

def save_summary_to_s3_bucket(summary:str, s3_bucket, s3_key):
    s3 = boto3.client('s3')
    try:
        s3.put_object(Body=summary, Bucket=s3_bucket, Key=s3_key)
        print(f"Summary Saved to s3")

    except Exception as e:
        print(f"Error saving summary to S3: {e}")

def lambda_handler(event, context):
    
    decoded_body = base64.b64decode(event['body'])

    text_content = extract_text_from_multipart_(decoded_body)

    if not text_content:
        return {
            'statusCode': 400,
            'body': json.dumps('No text content found in the email')
        }

    generated_summary = generate_summary_from_bedrock(text_content)


    if generated_summary:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        s3_key = f'summary_output/{current_time}'
        s3_bucket = 'bedrock-course-bucket-01.txt'

        save_summary_to_s3_bucket(generated_summary, s3_bucket, s3_key)

    else:
        print('No summary was generated')

    return{
        'statusCode': 200,
        'body': json.dumps('Summary Generated and Saved to S3')
    }


    

    