import os
import boto3
from botocore.config import Config
import sys
from botocore.exceptions import (ClientError, EndpointConnectionError, NoCredentialsError, ConnectTimeoutError, ReadTimeoutError, ConnectionClosedError)

# 1. Retrieve credentials from environment variables
access_key = os.getenv("MINIO_ACCESS_KEY")
secret_key = os.getenv("MINIO_SECRET_KEY")
endpoint_url = os.getenv("MINIO_ENDPOINT")
config = Config(
    signature_version = 'v4',
    connect_timeout=5,
    read_timeout=10,
    retries={
        "max_attempts": 3, 
        "mode": "standard"
        } 
)

#catch credential errors
if not all([access_key, secret_key, endpoint_url]):
    print("Missing MinIO credentials. Please set the environment variables.")
    sys.exit("Exiting due to missing credentials.")

print("Creating S3 client...")
s3_client = boto3.client(
    "s3",
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    endpoint_url=endpoint_url,
    config=config
)

# 3. Connect to your MinIO endpoint
def connect_to_minio(s3_client):
    try:
        response = s3_client.list_buckets()
        print("Connected to MinIO successfully.")
        # 4. List buckets
        for bucket in response.get('Buckets', []):
            print(f"Bucket Name: {bucket['Name']}")
    #5 . Handle exceptions for connection, timeouts , and credential errors
    except EndpointConnectionError as e:
        print(f"Endpoint Connection Error:, {e}")
        sys.exit("Exiting due to connection error.")
    except (ConnectTimeoutError, ConnectionClosedError, ReadTimeoutError) as e:
        print(f"MinIO Connection Timeout Error:, {e}")
        sys.exit("Exiting due to connection error.") 
    except NoCredentialsError as e:
        print(f"No credential Error:, {e}")
        sys.exit("Exiting due to connection error.") 
    except ClientError as e:
        print(f"Client Error:, {e}")
        sys.exit("Exiting due to connection error.")  

connect_to_minio(s3_client)