import requests
import json

# API URL
from dotenv import load_dotenv
import os
# Load environment variables from .env file
load_dotenv()

# The API endpoint where you need to send the request

api_key = os.getenv("FLIKI_API_KEY")
# from .pycountry_test import all_dialects 
# all_dialects()
# Headers
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
def get_langunages():
    url = "https://api.fliki.ai/v1/languages"

    # Making a GET request
    response = requests.get(url, headers=headers)

    # Checking the response
    if response.status_code == 200:
        print(response.json())
        response_data = response.json()
        return {"success":True,**response_data}

    else:
        error_data = response.json()
        return {"success":False,"error":error_data}

def get_dialects():
    url = "https://api.fliki.ai/v1/dialects"

    # Making a GET request
    response = requests.get(url, headers=headers)

    # Checking the response
    if response.status_code == 200:
        print(response.json())
        response_data = response.json()
        return {"success":True,**response_data}

    else:
        error_data = response.json()
        return {"success":False,"error":error_data}

def get_voices(language_id, dialect_id, gender):
    url = "https://api.fliki.ai/v1/voices"
    payload = {
        "languageId": language_id,
        "dialectId": dialect_id
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        response_data = response.json()
        # Check if 'data' key exists in the response
        if 'data' in response_data:
            # Filter voices by gender
            filtered_voices = [voice for voice in response_data['data'] if voice['gender'] == gender.upper()]
            return {"success": True, "data": filtered_voices}
        else:
            return {"success": False, "error": "No data key in response"}
    else:
        error_data = response.json()
        return {"success": False, "error": error_data}
from .models import Dialect, Language
import re

def load_data_from_json():
    with open('chat_openai/dialect.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    for item in data['data']:
        full_name = item['name']

        # Extract the first two letters of the name
        initials = full_name[:2]

        # Extract the part of the name after the first space
        name_post_space = full_name.split(' ', 1)[1] if ' ' in full_name else ''

        dialect, created = Dialect.objects.get_or_create(
            _id=item['_id'],
            defaults={
                'name': full_name, 
                'name_post_space': name_post_space,
                'initials': initials
            }
        )

        if created:
            print(f'Added new dialect: {dialect.name}')
        else:
            print(f'Dialect already exists: {dialect.name}')


# load_data_from_json()

def create_video(text_input, voice_id, aspectratio, bg_music):
    # Define accepted aspect ratios
    accepted_aspect_ratios = ['landscape', 'portrait', 'square']

    # Check if the provided aspect ratio is valid, default to 'square' if not
    aspectratio = aspectratio if aspectratio in accepted_aspect_ratios else 'square'

    url = "https://api.fliki.ai/v1/generate"
    payload = {
        "format": "video",
        "scenes": [
            {
                "content": text_input,  # Replace with your actual content
                "voiceId": voice_id     # Replace with the actual voice ID
            }
        ],
        "settings": {'aspectRatio': aspectratio},
        "backgroundMusicKeywords": bg_music  # Replace with actual keywords
    }
    # Making a GET request
    response = requests.post(url, json=payload, headers=headers)
    print(response.json())
    if response.status_code == 200:
        try:
            response_data = response.json()
            if 'id' in response_data['data']:
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

# create_video('a cozy company that every body are smoking in it', '61cb51510b30e7b67204839b', 'portrait', 'lofi')    
def get_status(video_id):
    # API URL
    url = "https://api.fliki.ai/v1/generate/status"

    # Your API key

    # Payload data
    payload = {
        "id": f"{video_id}"  # Replace with your actual ID
    }
    # Making a POST request
    response = requests.post(url, headers=headers, json=payload)

    # Checking the response
    if response.status_code == 200:
        response_data = response.json()
        print(response.json())
        return {"success":True,'data':response_data}

    else:
        error_data = response.json()
        return {"success":False,"error":error_data}
# get_status("65881b4fc5d28dabf9141db9")


def generate_text_to_speech(content, voice_id):
    url = "https://api.fliki.ai/v1/generate/text-to-speech"
    payload = {
        "content": content,
        "voiceId": voice_id,
        # "voiceStyleId": voice_style_id
    }
    response = requests.post(url, headers=headers, json=payload)
    print(response.status_code)
    if response.json()['success'] == True:
        print(response.json())
        response_data = response.json()
        return {"success":True,'data':response_data}

    else:
        error_data = response.json()
        print(error_data)
        return {"success":False,"error":error_data}
        
# generate_text_to_speech('سامان. داداش یکم صبر داشته باش ','61b8b4814268666c126bb3ef')

def generate_text_to_image(content, style):
    url = "https://api.fliki.ai/v1/generate/text-to-image"
    payload = {
        "content": content,
        "style": style
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        response_data = response.json()
        print(response.json())
        return {"success":True,'data':response_data}
    else:
        error_data = response.json()
        return {"success":False,"error":error_data}

# get_langunages()
# get_dialects()
# get_voices()
# create_video()
# get_status("6582b5547dfd314748c0724e")

# generate_text_to_image('A MAN FLYING', '3d-model')