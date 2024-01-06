import requests
import base64
from dotenv import load_dotenv
import os
# Load environment variables from .env file
load_dotenv()

# The API endpoint where you need to send the request

api_key = os.getenv("STUDIO_API_KEY")
username = os.getenv("STUDIO_USERNAME")
password = os.getenv("STUDIO_PASSWORD")


# Encode the username and password
credentials = f"{username}:{password}"
encoded_credentials = base64.b64encode(credentials.encode()).decode()

# Headers with encoded credentials
headers = {
    "Authorization": f"Basic {credentials}"
}

# "config": {
#             "stitch": True
#         }

import requests
import json

def create_talk(text_input, image, fluent, expression, speed_rate, voice_id):
    url = "https://api.d-id.com/talks"

    payload = {
        "script": {
            "type": "text",
            "subtitles": False,
            "provider": {
                "type": "microsoft",
                "voice_id": voice_id,
                "voice_config": {"rate": speed_rate}
            },
            "ssml": "false",
            "input": text_input
        },
        "config": {
            "fluent": fluent,
            "pad_audio": "0.0",
            "driver_expressions": {
                "expressions": [
                    {
                        "expression": expression,
                        "start_frame": 0,
                        "intensity": 1
                    }
                ]
            },
            "result_format": "mp4",
            "normalization_factor": 1
        },
        "source_url": image
    }

    response = requests.post(url, json=payload, headers=headers)
    print(response.status_code)
    if response.status_code == 201:
        try:
            response_data = response.json()
            if 'id' in response_data and 'status' in response_data and response_data['status'] == 'created':
                return {"success": True, "data": response_data}
            else:
                return {"success": False, "error": "Unexpected response format"}
        except json.JSONDecodeError:
            return {"error": "Invalid JSON in response"}
    else:
        try:
            error_data = response.json()
            return {"error": error_data}
        except json.JSONDecodeError:
            return {"error": "Non-200 status code received without valid JSON error message"}


# create_talk('something in the way is in my throut hahaha','https://app.flxdevpanel.com/media/test.jpg',True,'happy','0.5')

def get_talk(talk_id):
    api_url = f"https://api.d-id.com/talks/{talk_id}"
    response = requests.get(api_url,headers=headers)
    if response.status_code == 200:
        response_data = response.json()
        print("Request successful.")
        print("Response data:", response.json())
        return {"success":True,**response_data}

    else:
        error_data = response.json()
        print("Request failed.")
        print("Status code:", response.status_code)
        print("Response:", response.text) 
        return {"success":False,"error":error_data}



def get_talks():
    api_url = f"https://api.d-id.com/talks/"
    response = requests.get(api_url,headers=headers)
    if response.status_code == 200:
        print("Request successful.")
        print("Response data:", response.json())
    else:
        print("Request failed.")
        print("Status code:", response.status_code)
        print("Response:", response.text) 






# clips --------------------------------------------------

def create_clip(text_input,presenter_id,driver_id,bg_color):
    api_url = "https://api.d-id.com/clips"
    # Data to be sent in the API request
    data = {
        "script": {
            "type": "text",
            "input": text_input
        },
        "presenter_id": presenter_id,
        "driver_id": driver_id,
        "background": {
        "color": bg_color
        }
    }

    # Making a POST request to the API
    response = requests.post(api_url,headers=headers, json=data)

    # Checking if the request was successful
    if response.status_code == 201:
        response_data = response.json()
        print("Request successful.")
        print("Response data:", response.json())
        return {"success":True,'data':response_data}

    else:
        response_data = response.json()
        print("Request failed.")
        print("Status code:", response.status_code)
        print("Response:", response.text)
        return {"success":False,'error':response_data}  

# create_clip("somthing in the way","diana-tfTP6K9S9u","6aL7yccFTg","#ffffff")

def get_clip(clip_id):
    api_url = f"https://api.d-id.com/clips/{clip_id}"
    response = requests.get(api_url,headers=headers)
    if response.status_code == 200:
        response_data = response.json()
        response_data.pop('owner_id',None)
        print("Request successful.")
        print("Response data:", response.json())
        return {"success":True,**response_data}

    else:
        response_data = response.json()
        print("Request failed.")
        print("Status code:", response.status_code)
        print("Response:", response.text) 
        return {"success":False,'error':response_data}  


def get_clips():
    api_url = f"https://api.d-id.com/clips/"
    response = requests.get(api_url,headers=headers)
    if response.status_code == 200:
        print("Request successful.")
        print("Response data:", response.json())
    else:
        print("Request failed.")
        print("Status code:", response.status_code)
        print("Response:", response.text) 


def get_actors():
    api_url = f"https://api.d-id.com/clips/actors/"
    response = requests.get(api_url,headers=headers)
    if response.status_code == 200:
        print("Request successful.")
        print("Response data:", response.json())
    else:
        print("Request failed.")
        print("Status code:", response.status_code)
        print("Response:", response.text) 

def get_actor_drivers(actor_id):
    api_url = f"https://api.d-id.com/clips/actors/{actor_id}/drivers/"
    response = requests.get(api_url,headers=headers)
    if response.status_code == 200:
        print("Request successful.")
        print("Response data:", response.json())
    else:
        print("Request failed.")
        print("Status code:", response.status_code)
        print("Response:", response.text) 


def get_presenter_drivers(presenter_id):
    api_url = f"https://api.d-id.com/clips/presenters/{presenter_id}/drivers"
    response = requests.get(api_url,headers=headers)
    if response.status_code == 200:
        response_data = response.json()
        print("Request successful.")
        print("Response data:", response.json())
        response_data = response.json()

        return {"success":True,**response_data}
    else:
        response_data = response.json()
        print("Request failed.")
        print("Status code:", response.status_code)
        print("Response:", response.text) 
        return {"success":False,'error':response_data}  


def get_presenters(limit):
    api_url = f"https://api.d-id.com/clips/presenters?limit={limit}"
    response = requests.get(api_url,headers=headers)
    if response.status_code == 200:
        response_data = response.json()
        response_data.pop('token', None)
        print("Request successful.")
        return {"success":True,**response_data}
    else:
        response_data = response.json()
        print("Request failed.")
        print("Status code:", response.status_code)
        return {"success":False,'error':response_data}

















# animation

def get_animation(animation_id):
    print(animation_id)
    api_url = f"https://api.d-id.com/animations/{animation_id}"
    response = requests.get(api_url,headers=headers)
    if response.status_code == 200:
        response_data = response.json()
        print("Request successful.")
        print("Response data:", response.json())
        return {"success":True,**response_data}
    else:
        response_data = response.json()
        print("Request failed.")
        print("Status code:", response.status_code)
        return {"success":False,'error':response_data}

# get_animation("anm_hqK-5-K0dePLuJFEqaUuG")
def create_animation(image_url):
    url = "https://api.d-id.com/animations"

    payload = {
        "config": { "result_format": "mp4" },
        "source_url": image_url
    }


    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 201:
        response_data = response.json()
        print("Request successful.")
        print("Response data:", response.json())
        return {"success":True,'data':response_data}

    else:
        response_data = response.json()
        print("Request failed.")
        print("Status code:", response.status_code)
        print("Response:", response.text)
        return {"success":False,'error':response_data}  

# create_animation("https://app.flxdevpanel.com/media/test.jpg")
# talks 
# get_talk("tlk_9RomgIQPudk9OBb9DrrnJ")
# get_talk("tlk_4kSV4co4tFZVymfmKospR")
# create_stitch_talk()
# get_talks()
# create_talk_with_config()
# create_talk_config2()
# get_talk("tlk_FHTOGXUo2zeRGPuBUdhoz")

# clips 
# create_clips()
# get_clip("clp_Q3BSbMuL4XNKmfrVNUUop")
# get_clips()
# get_actors()
# get_actor_drivers("arran")
# get_presenters_drivers("arran")


# animation
# get_animation("anm_I-J-npsqLKWh7JYWLxZgj")
# create_animation()