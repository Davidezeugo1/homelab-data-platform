import responses
import requests
import pytest
from src.extract import fetch_weather

@responses.activate
def test_fetch_weather_success():
    url = "https://api.open-meteo.com/v1/forecast"

    responses.add(
        responses.GET,
        url,
        json={
            "current" : {
                "temperature_2m" : 23.5
            }
        },
        status = 200
    )
    data = fetch_weather(url, params={})

    assert isinstance(data, dict)
    assert data["current"]["temperature_2m"] == 23.5


@responses.activate
def test_fetch_weather_retry_after_429(monkeypatch):
    url = "https://api.open-meteo.com/v1/forecast"
        
    monkeypatch.setattr("src.extract.time.sleep", lambda seconds: None)
    responses.add(
        responses.GET,
        url,
        status = 429,
        headers={"Retry-After": "1"} 
    )
    responses.add(
        responses.GET,
        url,
        json={
            "current" : {
                "temperature_2m" : 23.5
            }
        },
        status = 200
    )
    
    data = fetch_weather(url, params={})

    assert data["current"]["temperature_2m"] == 23.5
    assert len(responses.calls) == 2

@responses.activate
def test_fetch_weather_connection_error(monkeypatch):
    url = "https://api.open-meteo.com/v1/forecast"

    #prevent real waiting
    monkeypatch.setattr("src.extract.time.sleep", lambda seconds: None)

    responses.add(
        responses.GET,
        url,
        body=requests.exceptions.ConnectionError("Timeout error")
        )

    responses.add(
        responses.GET,
        url,
        json = {"current": {"temperature_2m" : 23.5}},
        status=200
    )

    data = fetch_weather(url, params={})

    assert data["current"]["temperature_2m"] == 23.5
    assert len(responses.calls) == 2

@responses.activate
def test_fetch_weather_http_500():
    url = "https://api.open-meteo.com/v1/forecast"
    responses.add(
        responses.GET,
        url,
        json={"error": "Internal Server Error"},
        status=500
    )

    with pytest.raises(requests.exceptions.HTTPError):
        fetch_weather(url, params={})
    assert len(responses.calls) == 1


