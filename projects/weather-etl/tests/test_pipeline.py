from unittest.mock import Mock, patch, call
from pathlib import Path
import pytest 

from src.pipeline import run_weather_pipeline


def test_run_weather_pipeline():

    # Simulate the data returned by the API
    fake_data = {
        "latitude": 38.961170,
        "longitude": -92.376362,
        "current": {
            "time": "2026-11-10T12:00",
            "temperature_2m": 18.5
        },
        "current_units": {
            "temperature_2m": "°C"
        }
    }

    # Simulate the local file returned by storage
    saved_file = (Path("data/raw/weather.json"), "weather_test")

    # Simulate the MinIO object keys
    raw_key = "weather/weather_test.json"
    validated_key = "weather/weather_test.json"

    # Simulate an S3 client
    s3_client = Mock()

    output_dir = Path("data/raw")

    # Mock each pipeline stage
    with patch("src.pipeline.fetch_weather", return_value=fake_data) as fetch_mock, \
         patch("src.pipeline.save_raw_data_local", return_value=saved_file) as raw_mock, \
         patch("src.pipeline.upload_to_minio", return_value=raw_key) as upload_mock, \
         patch("src.pipeline.weather_validation", return_value=(18.5, "Success")) as validation_mock, \
         patch("src.pipeline.save_validated_data_to_minio", return_value=validated_key) as validated_mock:

        # Track the order in which the functions execute
        pipeline_calls = Mock()
        pipeline_calls.attach_mock(fetch_mock, "fetch")
        pipeline_calls.attach_mock(raw_mock, "save_raw")
        pipeline_calls.attach_mock(upload_mock, "upload_raw")
        pipeline_calls.attach_mock(validation_mock, "validate")
        pipeline_calls.attach_mock(validated_mock, "upload_validated")

        result = run_weather_pipeline(
            "https://api.open-meteo.com/v1/forecast",
            {
                "latitude": 38.961170,
                "longitude": -92.376362,
                "current": "temperature_2m"
            },
            s3_client,
            output_dir
        )

        # Verify each stage received the correct inputs
        fetch_mock.assert_called_once()
        raw_mock.assert_called_once_with(fake_data, output_dir)
        upload_mock.assert_called_once_with(s3_client, saved_file)
        validation_mock.assert_called_once_with(fake_data)
        validated_mock.assert_called_once_with(
            (18.5, "Success"),
            s3_client,
            saved_file,
            fake_data
        )

        # Verify execution order
        assert pipeline_calls.mock_calls == [
            call.fetch(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": 38.961170,
                    "longitude": -92.376362,
                    "current": "temperature_2m"
                }
            ),
            call.save_raw(fake_data, output_dir),
            call.upload_raw(s3_client, saved_file),
            call.validate(fake_data),
            call.upload_validated(
                (18.5, "Success"),
                s3_client,
                saved_file,
                fake_data
            )
        ]

        # Verify the pipeline summary
        assert result == {
            "status": "success",
            "raw_object_key": raw_key,
            "validated_object_key": validated_key
        }


def test_run_weather_pipeline_validation_failure():
    # 1. Create fake weather data with an invalid temperature
    fake_data = {
        "latitude": 38.961170,
        "longitude": -92.376362,
        "current": {
            "time": "2026-11-10T12:00",
            "temperature_2m": "unknown"
        },
        "current_units": {
            "temperature_2m": "°C"
        }
    }

    # 2. Create a fake saved-file tuple
    save_file = (Path("data/raw/weather.json"), "weather_test")
    raw_key = ("weather/weather_test")


    # 3. Create a fake S3 client
    s3_client= Mock()
    output_dir = Path("data/raw")


    with patch("src.pipeline.fetch_weather", return_value = fake_data) as fetch_mock, \
        patch("src.pipeline.save_raw_data_local", return_value= (save_file)) as raw_mock, \
        patch("src.pipeline.upload_to_minio", return_value= raw_key) as upload_mock, \
        patch ("src.pipeline.weather_validation", return_value= (None, "ERROR: temperature_2m is not a number." )) as validate_mock:
        #patch ("src.pipeline.save_validated_data_to_minio", return_value= validated_key) as validated_mock:

        # 8. Run the pipeline and expect ValueError
        with pytest.raises(ValueError, match= "Validation failed"):
            run_weather_pipeline(
                "https://api.open-meteo.com/v1/forecast",
                {
                    "latitude": 38.961170,
                    "longitude": -92.376362,
                    "current": "temperature_2m"
                },
                s3_client,
                output_dir
            )


        # 9. Verify raw data was uploaded
        fetch_mock.assert_called_once()
        raw_mock.assert_called_once_with(fake_data, output_dir)
        upload_mock.assert_called_once_with(s3_client, save_file)

        # 10. Verify validated data was NOT uploaded
        validate_mock.assert_called_once_with(fake_data)
        s3_client.put_object.assert_not_called()
        

        

