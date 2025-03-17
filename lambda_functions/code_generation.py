import boto3
import botocore.config
import json
from datetime import datetime

def generate_code_using_bedrock(message: str, language: str) -> str:
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
                "content": f"Create a {language} code for the following instructions: {message}"
            }
        ]
    }

    try:
        bedrock = boto3.client("bedrock-runtime", 
                                region_name="us-west-2", 
                                config=botocore.config.Config(read_timeout=300, 
                                                              retries={"max_attempts": 3}))

        response = bedrock.invoke_model(
            body=json.dumps(request_body), 
            modelId="anthropic.claude-3-5-sonnet-20241022-v2:0"
        )
        response_content = response.get("body").read().decode("utf-8")
        response_data = json.loads(response_content)
        
        # Extract the code from the response
        code = response_data["content"][0]["text"]
        return code
    
    except Exception as e:
        print(f"Error: {e}")
        return None

def save_code_to_s3_bucket(code, s3_bucket, s3_key):
    s3 = boto3.client("s3")
    try:
        s3.put_object(Bucket=s3_bucket, Key=s3_key, Body=code)
        print("Code saved to s3")
    
    except Exception as e:
        print(f"Error: {e}")

def lambda_handler(event, context):
    event = json.loads(event["body"])
    message = event["message"]
    language = event["key"]
    print(message, language)
    
    generated_code = generate_code_using_bedrock(message, language)

    if generated_code:
        current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        s3_key = f'code-output/{current_time}.py'
        s3_bucket = 'bedrock-course-bucket-01'

        save_code_to_s3_bucket(generated_code, s3_bucket, s3_key)
    
    else:
        print('No code was generated')
    
    return {
        'statusCode': 200,
        'body': json.dumps('Code generated and saved to s3')
    }