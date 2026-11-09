from src.validation import weather_validation
import pytest


@pytest.mark.parametrize("valid_temperature", [23.5, -5.0, 18])
def test_valid_temperature(valid_temperature):
    data = {
        "current": {
            "temperature_2m": valid_temperature
        }
    }

    temperature, message = weather_validation(data)

    assert temperature == valid_temperature
    assert message == "Success"

def test_missing_temperature():
    data = {"current": {}}

    temperature, message = weather_validation(data)

    assert temperature is None
    assert message == "ERROR: temperature_2m not found in the inner dictionary."

@pytest.mark.parametrize("invalid_temperature", [True, "true"])
def test_invalid_temperature_type(invalid_temperature):
    data = {
        "current": {
            "temperature_2m": invalid_temperature
        }
    }

    temperature, message = weather_validation(data)

    assert temperature is None
    assert message == "ERROR: temperature_2m is not a number."


def test_missing_current_key():
    data = {}

    temperature, message = weather_validation(data)

    assert temperature is None
    assert message == "ERROR: The 'current' key does not contain a dictionary."

def test_list_type():
    data = ["current","temperature_2m","true"]

    temperature, message = weather_validation(data)

    assert temperature is None
    assert message == "ERROR: The json is not a dictionary."

def test_current_key_dict():
    data = {"current": "not a dictionary"}

    temperature, message = weather_validation(data)

    assert temperature is None
    assert message == "ERROR: The 'current' key does not contain a dictionary."