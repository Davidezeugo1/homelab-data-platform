import pytest
import json
from unittest.mock import Mock
from src.storage import save_raw_data_local, save_validated_data_to_minio, upload_to_minio

def test_raw_data_save_local(tmp_path):
    data = {"current":{"temperature_2m" : 23.5}}
    file_path, timestamp = save_raw_data_local(
        data,
        output_dir = tmp_path/"raw"
    )

    with file_path.open("r", encoding="utf-8") as f:
        saved_data = json.load( f)

    assert file_path.exists()
    assert saved_data == data
    assert timestamp in file_path.name

def test_upload_to_minio(tmp_path):
    s3_client = Mock()

    file_path = tmp_path / "weather_test.json"

    file_path.write_text(
        '{"current" : {"temperature_2m" : 23.5}}',
        encoding = "utf-8"
    )
    saved_file = (file_path, "weather_test")

    object_key = upload_to_minio(s3_client, saved_file)

    assert s3_client.upload_file.call_count == 1
    assert object_key == "weather/weather_test.json"
    s3_client.upload_file.assert_called_once_with(
        Filename=str(file_path),
        Bucket="raw-data",
        Key="weather/weather_test.json"
    )

# def test_save_validated_data_to_minio(tmp_path):
#     s3_client = Mock()

#     result= (23.5, "Success")

#     file_path= (None, "weather_test")

#     data = {
#         "latitude": 38.96,
#         "longitude": -92.37,
#         "current": {
#             "time": "2026-11-10T10:00",
#         },
#         "current_units": {
#             "temperature_2m": "°C"
#         }
#     }

#     object_key = save_validated_data_to_minio(result, s3_client, file_path, data)

#     s3_client.put_object.assert_called_once_with(
#         Bucket= "validated-data",
#         Key= "weather/weather_test.json",
#         ContentType= "application/json"
#     )

#     assert s3_client.bucket == "validated-data"
#     assert object_key == None
#     assert s3_client.ContentType == "application/json"
#     assert result == 23.5

def test_save_validated_data_to_minio():
    s3_client = Mock()

    result = (23.5, "Success")
    file_path = (None, "weather_test")

    data = {
        "latitude": 38.96,
        "longitude": -92.37,
        "current": {
            "time": "2026-11-10T10:00",
        },
        "current_units": {
            "temperature_2m": "°C"
        }
    }

    object_key = save_validated_data_to_minio(
        result, s3_client, file_path, data
    )

    # Verify the upload happened once
    s3_client.put_object.assert_called_once()

    # Inspect the arguments sent to MinIO
    upload_args = s3_client.put_object.call_args.kwargs

    assert upload_args["Bucket"] == "validated-data"
    assert upload_args["Key"] == "weather/weather_test.json"
    assert upload_args["ContentType"] == "application/json"

    # Decode the JSON string sent to MinIO
    uploaded_data = json.loads(upload_args["Body"])

    assert uploaded_data["current"]["temperature"] == 23.5
    assert uploaded_data["current"]["message"] == "Success"

    assert object_key == "weather/weather_test.json"