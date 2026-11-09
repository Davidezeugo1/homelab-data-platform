#import libraries
import sys

def weather_validation(data: dict):

    if not isinstance(data, dict):
        return None, "ERROR: The json is not a dictionary."

    current = data.get("current")
    if not isinstance(current, dict):
        return None, "ERROR: The 'current' key does not contain a dictionary."
    
    if "temperature_2m" not in current: 
        return None, "ERROR: temperature_2m not found in the inner dictionary."
    
    temperature = current["temperature_2m"]
    if not isinstance(temperature, (int, float)) or isinstance(temperature, bool):
        return None, "ERROR: temperature_2m is not a number."
    
    return temperature, "Success"


# function to validate temperature and print the result
def validated_temp(result):
    temperature, message = result
    if temperature is None: 
        sys.exit(message) 
         
    else:
        print("Extraced current temp..")
        print (f"Current temperature: {temperature}°C")