import json
import logging
from datetime import datetime, timezone
from src.pipeline import create_s3_client, url, params
from src.extract import fetch_weather
from src.validation import weather_validation

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

def extract_weather():

    logger.info("Starting weather extraction")
    # 1. Creating S3 client
    s3_client = create_s3_client()

    # 2. Fetch weather data
    try:
        data = fetch_weather(url, params)
    except Exception:
        logger.exception("Could not fetch weather_data")
        raise 

    # 3. Generate a unique object key
# 3. Generate a deterministic object key
    timestamp = datetime.strptime(
        data["current"]["time"], "%Y-%m-%dT%H:%M"
    ).strftime("%Y%m%d_%H%M")

    latitude = data["latitude"]
    longitude = data["longitude"]

    raw_object_key = f"weather/{latitude}_{longitude}/{timestamp}.json"
    
    # 4. Convert dictionary to JSON
    weather_json = json.dumps(data, indent=4)

    # 5. Upload raw JSON to MinIO
    try:
        s3_client.put_object(
            Bucket="raw-data",
            Key=raw_object_key,
            Body=weather_json,
            ContentType="application/json"
        )
    except Exception:
        logger.exception("Failed to upload raw weather data to MinIO")
        raise

    logger.info(
        "Raw weather data uploaded to MinIO: %s",
        raw_object_key
    )

    # 6. Return object key for the next Airflow task
    return raw_object_key

def validate_weather(raw_object_key):

    logger.info("Starting data validation")
    # 1. Create S3 client
    s3_client = create_s3_client()

    # 2. Download raw JSON from MinIO
    try:
        response = s3_client.get_object(
            Bucket="raw-data",
            Key=raw_object_key
        )
    except Exception:
        logger.exception("Failed to download raw data from MinIO")
        raise

    # 3. Convert JSON text into a Python dictionary
    try:
        data = json.loads(response["Body"].read().decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        logger.exception("Failed to Decode raw weather JSON")
        raise
    # 4. Validate the weather data
    temperature, message = weather_validation(data)

    # 5. Stop the task if validation fails
    if temperature is None:
        logger.error("Weather validation failed: %s", message)
        raise ValueError(message)

    # 6. Build a small validated result
    validated_weather = {
        "latitude": data.get("latitude"),
        "longitude": data.get("longitude"),
        "time": data.get("current", {}).get("time"),
        "temperature": temperature,
        "units": data.get("current_units", {}).get("temperature_2m"),
        "message": message
    }

    logger.info(
        "Validation Passed"
    )

    # 7. Return the validated result
    return validated_weather

def store_weather(validated_weather, raw_object_key):

    logger.info("Storing data to MinIO")
    # 1. Create S3 client
    s3_client = create_s3_client()

    # 2. Reuse the original filename for traceability
    filename = raw_object_key.split("/")[-1]
    validated_object_key = f"weather/{filename}"

    # 3. Convert validated dictionary to JSON
    try:
        validated_json = json.dumps(validated_weather, indent=4)
    except (TypeError, ValueError):
        logger.exception("Failed to encode validated weather to JSON")
        raise
    
    # 4. Upload validated JSON to MinIO
    try:
        s3_client.put_object(
            Bucket="validated-data",
            Key=validated_object_key,
            Body=validated_json,
            ContentType="application/json"
        )
    except Exception:
        logger.exception("Failed to upload validated weather data to MinIO")
        raise

    logger.info("Validated data uploaded to MinIO: %s",
        validated_object_key
    )
    # 5. Return the validated object key
    return validated_object_key

if __name__ == "__main__":
    raw_object_key = extract_weather()
    valid_weather = validate_weather(raw_object_key)
    store_weather_data = store_weather(valid_weather, raw_object_key)
    print(f"Extraction successful: {raw_object_key}")
