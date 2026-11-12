import os 
import boto3
from pathlib import Path 
from botocore.config import Config
from src.extract import fetch_weather
from src.validation import weather_validation
from src.storage import (
    save_raw_data_local,
    upload_to_minio,
    save_validated_data_to_minio
)

url =  "https://api.open-meteo.com/v1/forecast"

params = {
    'latitude' : 38.961170,
    'longitude' : -92.376362,
    'current' : 'temperature_2m'
}

def create_s3_client():

    #Retrieve credentials from environment variables
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
        raise ValueError("Exiting due to missing credentials.")

    #create S3 client
    return boto3.client(
        "s3",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        endpoint_url=endpoint_url,
        config=config
    )

def run_weather_pipeline(url, params, s3_client, output_dir=Path("data/raw")):
   
    # 1. Extract
    data = fetch_weather(url, params=params)
    
    # 2. Save raw data locally 
    save_file = save_raw_data_local(data,output_dir)
    
    # 3. Upload raw data to MinIO
    raw_object_key = upload_to_minio(s3_client, save_file) 
    
    # 4. Validate
    validated_weather= weather_validation(data)

    # 5. Upload validated data to MinIO
    validated_object_key = save_validated_data_to_minio(validated_weather, s3_client, save_file, data)
    
    # 6. Return execution summary
    return {
        "status": "success",
        "raw_object_key": raw_object_key,
        "validated_object_key": validated_object_key
    }

