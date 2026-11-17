
import json
import logging
from datetime import datetime
from pathlib import Path
from botocore.exceptions import (
    ClientError,
    BotoCoreError,
)

logger = logging.getLogger(__name__)


def save_raw_data_local(data: dict, output_dir=Path("data/raw")):
    try:
        timestamp = f"weather_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        file_path = output_dir / f"{timestamp}.json"

        with file_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        logger.info("Raw weather data saved locally: %s", file_path)

        return file_path, timestamp

    except (OSError, TypeError, ValueError):
        logger.exception("Failed to save raw weather data locally")
        raise


def upload_to_minio(s3_client, save_file):
    file_path, timestamp = save_file
    object_key = f"weather/{timestamp}.json"

    try:
        s3_client.upload_file(
            Filename=str(file_path),
            Bucket="raw-data",
            Key=object_key
        )

        logger.info("Raw data uploaded to MinIO: %s", object_key)

        return object_key

    except (ClientError, BotoCoreError, OSError):
        logger.exception("Failed to upload raw data to MinIO")
        raise


def save_validated_data_to_minio(result, s3_client, save_file, data):
    _, timestamp = save_file
    temperature, message = result

    if temperature is None:
        raise ValueError(
            "Validation failed. Temperature is missing or invalid."
        )

    try:
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
            Bucket="validated-data",
            Key=object_key,
            Body=json.dumps(message_body, indent=4),
            ContentType="application/json"
        )

        logger.info("Validated data uploaded to MinIO: %s", object_key)

        return object_key

    except (ClientError, BotoCoreError, TypeError, ValueError):
        logger.exception("Failed to upload validated data to MinIO")
        raise
