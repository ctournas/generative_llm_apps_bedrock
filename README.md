# AWS Bedrock with Lambda, API Gateway, and Postman

## Overview
This project demonstrates how to integrate AWS Bedrock with AWS Lambda, API Gateway, and Postman for AI-based inference tasks. It provides multiple functionalities including:

- **Text-to-Image Generation** using Stability AI models.
- **Meeting Summary Generation** using Anthropic Claude models.
- **Code Generation** for different programming languages.

The generated outputs (images, summaries, or code snippets) are stored in an S3 bucket.

## Architecture
The solution is built using:
- **AWS Bedrock**: AI model inference (Stability AI & Anthropic Claude).
- **AWS Lambda**: Serverless compute function handling API requests.
- **Amazon S3**: Storage for generated outputs.
- **API Gateway**: RESTful interface to invoke the Lambda function.
- **Postman**: Testing API endpoints.
