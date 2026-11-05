#import the libaries 
import requests
import json 
from datetime import datetime
import sys
import time
import responses

# set the URL and parameters for the API request
url =  "https://api.open-meteo.com/v1/forecast"

params = {
    'latitude' : 38.961170,
    'longitude' : -92.376362,
    'current' : 'temperature_2m'
}

# request and handle the response with error handling for connectoin issues, timeout, and HTTP errors
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
            break  # Exit the loop if the request was successful 
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


#create timestamp
timestamp = f"weather_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# 1. Define the correct path
file_path = f'data/raw/{timestamp}.json'
print("loading raw data to .josn file")

#Open file and save the raw json
with open(file_path, "w") as f:
    json.dump(data, f, indent=4)


# function to validate the json data is correct
print("loading date for validation...")
def validate_weather(mydata: dict):

    if "current" in mydata:
        inner_dic = mydata.get("current")

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
        result = (None, "ERROR: The Json does't have the date we are looking for.")
        return result

# function to validate the json data is correct and upload to the new file location
def validate_temp(result):
    temperature, message = result
    if temperature is None: 
        print (message) 
    else:
        print("Extraced current temp..")
        print (f"Current temperature: {temperature}°C")


new_file_path = f'data/validate/{timestamp}.json'

def savetofile(data: dict):
    with open (new_file_path, "w") as file:
        print("saving the validated data to a new file...")
        temperature, message = validate_weather(data)
        cur_result = {
            "temperature": temperature,
            "units": "°C",
            "message": message
            }
        json.dump(cur_result, file, indent=4) 

#run both funcation
#savetofile(validate_temp(validate_weather(data)))
result = validate_weather(data)
validate_temp(result)
savetofile(data) 

#closing the file and checking if the file is closed or not
print (f"file was closed: {f.closed}")
