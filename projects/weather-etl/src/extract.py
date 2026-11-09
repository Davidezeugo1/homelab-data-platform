#import libraries
import requests
import time 

def fetch_weather(url, params) -> dict:
    for attempt in range(2):  # allow only 2 attempt 
        try:
            response = requests.get(url, params=params, timeout=(5,10))
            #Handle HTTP error 429(To manu request)
            if response.status_code == 429:
                print(f"Attempt {attempt + 1}...falied")
                retry_after= int(response.headers.get("Retry-After", 5))
                print(f"HTTP-Error(429) Rate limited. Waiting {retry_after} seconds...")

                if attempt < 1:
                    time.sleep(retry_after)
                    continue
                else:
                    raise RuntimeError("Weather API request failed after 2 attempts.")

            response.raise_for_status()  # Raise an exception for HTTP errors
            data = response.json()  # Convert the response to JSON format if no exceptions occurred
            if not isinstance(data, dict):
                raise ValueError("Weather API response must be a dictionary.")
            return data  #exit the loop if the request was successful
        except (requests.exceptions.ConnectTimeout,
                requests.exceptions.ConnectionError,
                requests.exceptions.ReadTimeout ) as net_e:
            print(f"Attempt {attempt + 1} failed: network error : {net_e}")

            if attempt < 1:
                print("\nRetrying...\n")
                time.sleep(2)  # Wait for 2 seconds before retrying
            else:
                raise 
            
        except requests.exceptions.HTTPError as http_e:
            print(f"error httperror : {http_e}")
            raise

        except requests.exceptions.JSONDecodeError as json_e:  
            print(f"error jsondecodeerror : {json_e}")
            raise

