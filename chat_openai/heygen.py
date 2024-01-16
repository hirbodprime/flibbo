import requests
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("HEYGEN_API_KEY")

headers = {
        'X-Api-Key': api_key,
        'Content-Type': 'application/json'
}

def create_video_heygen(bg_color,ratio,avatar_id,input_text,voice_id):
    # Request headers
    url = 'https://api.heygen.com/v1/video.generate'
    

    # Request data
    data = {
        "background": bg_color,
        "ratio": ratio,
        "test": False,
        "version": "v1alpha",
        "clips": [
            {
                "avatar_id": avatar_id,
                "avatar_style": "normal",
                "caption": False,
                "input_text": input_text,
                "scale": 1,
                "voice_id": voice_id,
                # "input_audio": "https://surreal-public.s3.us-east-2.amazonaws.com/text_to_speech/bmRnpHd9dyz8sE4ER2hDj4.wav",
                "talking_photo_style": "normal"
            }
        ],
    }
    # Make the POST request
    response = requests.post(url, json=data, headers=headers)

    # Check if the request was successful
    if response.status_code == 201:
        response_data = response.json()
        print("Request successful.")
        print("Response data:", response.json())
        return {"success":True,**response_data}

    else:
        response_data = response.json()
        print("Request failed.")
        print("Status code:", response.status_code)
        print("Response:", response.text)
        return {"success":False,**response_data} 


def get_video(video_id):

    url = f"https://api.heygen.com/v1/video_status.get?video_id={video_id}"

    response = requests.get(url, headers=headers)

    if response.status_code == 201:
        response_data = response.json()
        return {"success":True,**response_data}

    else:
        response_data = response.json()
        return {"success":False,**response_data} 




def add_caption(video_id):
    url = "https://api.heygen.com/v1/video/caption.generate"

    payload = { "video_id": video_id }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "x-api-key": api_key
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 201:
        response_data = response.json()
        return {"success":True,**response_data}

    else:
        response_data = response.json()
        return {"success":False,**response_data} 

def get_caption(video_id):
    url = f"https://api.heygen.com/v1/video/caption.get?video_id={video_id}"
    headers = {
        "accept": "application/json",
        "x-api-key": api_key
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 201:
        response_data = response.json()
        return {"success":True,**response_data}

    else:
        response_data = response.json()
        return {"success":False,**response_data} 


def list_avatars():

    # url = "https://api.heygen.com/v1/avatar.list"
    url = "https://api.heygen.com/v2/avatars"

    response = requests.get(url, headers=headers)

    if response.status_code == 201:
        response_data = response.json()
        return {"success":True,**response_data}

    else:
        response_data = response.json()
        return {"success":False,**response_data}


def list_voices():

    # url = "https://api.heygen.com/v1/voice.list"
    url = "https://api.heygen.com/v2/voices"

    response = requests.get(url, headers=headers)

    if response.status_code == 201:
        response_data = response.json()
        return {"success":True,**response_data}

    else:
        response_data = response.json()
        return {"success":False,**response_data}

    