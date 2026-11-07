#import the libaries 
import requests
import json 
from datetime import datetime
import sys
import os
import time
import boto3
from botocore.config import Config
from botocore.exceptions import (ClientError, EndpointConnectionError, NoCredentialsError, ConnectTimeoutError, ReadTimeoutError, ConnectionClosedError)


# set the URL and parameters for the API request
url =  "https://api.open-meteo.com/v1/forecast"
params = {
    'latitude' : 38.961170,
    'longitude' : -92.376362,
    'current' : 'temperature_2m'
}

# request and handle the response with error handling for connectoin issues, timeout, and HTTP errors
def fetch_weather(url, params):
    response = None
    #second attempt to compress the code
    for attempt in range(2):  # Retry up to 2 times
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
                        sys.exit("\nFailed after 2 attempts. Exiting program.")
                response.raise_for_status()  # Raise an exception for HTTP errors
                data = response.json()  # Convert the response to JSON format if no exceptions occurred
                print("Data Received!!")
                return data  #exit the loop if the request was successful
            except (requests.exceptions.ConnectTimeout,
                    requests.exceptions.ConnectionError,
                    requests.exceptions.ReadTimeout ) as net_e:
                print(f"Attempt {attempt + 1} failed: network error : {net_e}")
                if attempt < 1:
                    print("\nRetrying...\n")
                    time.sleep(2)  # Wait for 2 seconds before retrying
                if attempt == 1:  # If it's the last attempt, exit the program
                    sys.exit("\nFailed after 2 attempts. Exiting the program")
            except requests.exceptions.HTTPError as http_e:
                print(f"error httperror : {http_e}")
                sys.exit("\nExiting the program.") 
            except requests.exceptions.JSONDecodeError as json_e:  
                print(f"error jsondecodeerror : {json_e}")
                sys.exit("\nExiting the program.")

#Open file and save the raw json
def save_raw_data_local(data: dict): 
    #create timestamp and file path for the raw data
    timestamp = f"weather_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    file_path = f'data/raw/{timestamp}.json' 
    print(f"loading raw data to {file_path} file")
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)
    #closing the file and checking if the file is closed or not
    print (f"file was closed: {f.closed}")
    return file_path, timestamp # Return the file path and timestamp for further use


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
    print("Missing MinIO credentials. Please set the environment variables.")
    sys.exit("Exiting due to missing credentials.")

#create S3 client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    endpoint_url=endpoint_url,
    config=config
)

# Connect to your MinIO endpoint
def upload_to_minio(s3_client, file_path):
    file_path, timestamp = file_path # Unpack the tuple returned from save_raw_data_local
    try:
        s3_client.upload_file(
            Filename=file_path,
            Bucket="raw-data",
            Key=f"weather/{timestamp}.json"
        )
        print("Connected to MinIO successfully.")
        print(f"File uploaded to MinIO bucket to 'raw-data/weather/{timestamp}.json'")
    # Handle exceptions for connection, timeouts, and credential errors
    except EndpointConnectionError as e:
        print(f"Endpoint Connection Error:, {e}")
        sys.exit("Exiting due to connection error.")
    except (ConnectTimeoutError, ConnectionClosedError, ReadTimeoutError) as e:
        print(f"MinIO Connection Timeout Error:, {e}")
        sys.exit("Exiting due to connection error.") 
    except NoCredentialsError as e:
        print(f"No credential Error:, {e}")
        sys.exit("Exiting due to connection error.") 
    except ClientError as e:
        print(f"Client Error:, {e}")
        sys.exit("Exiting due to connection error.")  

# function to validate the json data is correct
def validate_weather(mydata: dict):
    print("loading date for validation...")
    if isinstance(mydata, dict):
       inner_dic = mydata.get("current")
       if isinstance(inner_dic, dict):
            if "temperature_2m" in inner_dic:
                val = inner_dic.get('temperature_2m')
                if isinstance (val, (int, float)) and not isinstance (val, bool):
                    result= (val,"Success")
                    return result
                else:
                    result= (None, "ERROR: temperature_2m is not a number.")
                    return result
            else:
                result =(None,"ERROR: temperature_2m not found in the inner dictionary.")
                return result
       else: 
            result = (None, "ERROR: The 'current' key does not contain a dictionary.")
            return result
    else:
        result = (None, "ERROR: The json is not a dictionary.")
        return result


# function to validate temperature and print the result
def validated_temp(result):
    temperature, message = result
    if temperature is None: 
        print (message) 
    else:
        print("Extraced current temp..")
        print (f"Current temperature: {temperature}°C")


def save_validated_to_minio(result, s3_client, file_path, data):
    file_path, timestamp = file_path # Unpack the tuple returned from save_raw_data_local
    temperature, message = result # Unpack the tuple returned 
    if temperature is not None:
        try:
            
            message_body ={
                "current": {
                    "latitude": data.get('latitude'),
                    "longitude": data.get('longitude'),
                    "time": data.get('current', {}).get('time'),
                    "temperature": temperature,
                    "units": data.get('current_units', {}).get('temperature_2m'),
                    "message": message
                }
            }

            json_file =json.dumps(message_body, indent=4)

            s3_client.put_object(
                Bucket= "validated-data",
                Key= f"weather/{timestamp}.json",
                Body= json_file,
                ContentType= "application/json" 
            )
            
            print("Connected to MinIO successfully.")
            print(f"Uploaded validated Temperature to 'validated-data/weather/{timestamp}.json'")
        # Handle exceptions for connection, timeouts, and credential errors
        except EndpointConnectionError as e:
            print(f"Endpoint Connection Error:, {e}")
            sys.exit("Exiting due to connection error.")
        except (ConnectTimeoutError, ConnectionClosedError, ReadTimeoutError) as e:
            print(f"MinIO Connection Timeout Error:, {e}")
            sys.exit("Exiting due to connection error.") 
        except NoCredentialsError as e:
            print(f"No credential Error:, {e}")
            sys.exit("Exiting due to connection error.") 
        except ClientError as e:
            print(f"Client Error:, {e}")
            sys.exit("Exiting due to connection error.")
    else:
        sys.exit("Validation failed. Temperature is missing or invalid.")
    
         

data = fetch_weather(url, params)
raw_file_path = save_raw_data_local(data)
upload_to_minio(s3_client, raw_file_path)
valid_weather_result = validate_weather(data)
validated_temp(valid_weather_result)
save_validated_to_minio(valid_weather_result, s3_client, raw_file_path, data)  

