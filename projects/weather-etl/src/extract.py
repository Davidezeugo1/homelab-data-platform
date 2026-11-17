#import libraries
import logging
import requests
import time

logger = logging.getLogger(__name__)


def fetch_weather(url, params) -> dict:
    for attempt in range(2):
        try:
            logger.info("Weather API request: attempt %s of 2", attempt + 1)

            response = requests.get(url, params=params, timeout=(5, 10))

            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 5))

                logger.warning(
                    "API rate limited. Waiting %s seconds.",
                    retry_after
                )

                if attempt < 1:
                    time.sleep(retry_after)
                    continue
                else:
                    raise RuntimeError(
                        "Weather API request failed after 2 attempts."
                    )

            response.raise_for_status()

            data = response.json()

            if not isinstance(data, dict):
                raise ValueError(
                    "Weather API response must be a dictionary."
                )

            logger.info("Weather API extraction successful")
            return data

        except (
            requests.exceptions.ConnectTimeout,
            requests.exceptions.ConnectionError,
            requests.exceptions.ReadTimeout
        ):
            if attempt < 1:
                logger.warning(
                    "Network error on attempt %s. Retrying...",
                    attempt + 1
                )
                time.sleep(2)
            else:
                logger.exception("Weather API network request failed")
                raise

        except requests.exceptions.HTTPError:
            logger.exception("Weather API returned an HTTP error")
            raise

        except requests.exceptions.JSONDecodeError:
            logger.exception("Weather API returned invalid JSON")
            raise