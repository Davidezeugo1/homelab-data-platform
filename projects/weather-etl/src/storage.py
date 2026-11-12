import json
from datetime import datetime
from pathlib import Path
import boto3
from botocore.config import Config
from botocore.exceptions import (ClientError, EndpointConnectionError, NoCredentialsError, ConnectTimeoutError, ReadTimeoutError, ConnectionClosedError)



#Open file and save the raw json
def save_raw_data_local(data: dict, output_dir=Path("data/raw")):
    # Create a unique timestamp
    timestamp = f"weather_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Create the directory if it doesn't exist
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Build the file path
    file_path = output_dir / f"{timestamp}.json"

    # Save the JSON data
    with file_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    return file_path, timestamp


def upload_to_minio(s3_client, save_file):
    file_path, timestamp = save_file # Unpack the tuple returned from save_raw_data_local
    object_key = f"weather/{timestamp}.json"


    s3_client.upload_file(
        Filename= str(file_path),
        Bucket="raw-data",
        Key= object_key
    )

    #print(f"Uploaded raw data to raw-data/{object_key}")

    return object_key


def save_validated_data_to_minio(result, s3_client, object_key, data):

    _, timestamp = object_key 
    temperature, message = result

    if temperature is None:
        raise ValueError(
            "Validation failed. Temperature is missing or invalid."
            )

    message_body = {
        "current": {
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
            "time": data.get("current", {}).get("time"),
            "temperature": temperature,
            "units": data.get("current_units", {}).get("temperature_2m"),
            "message": message
        }
    }

    object_key = f"weather/{timestamp}.json"

    s3_client.put_object(
        Bucket= "validated-data",
        Key= object_key,
        Body= json.dumps(message_body, indent=4),
        ContentType= "application/json"
    )

    #print(f"Uploaded validated data to validated-data/{object_key}")

    return object_key
