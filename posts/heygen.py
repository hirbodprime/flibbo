import requests


api_key = 'YmI3MGMzMjY5ZDNjNGFkMWI2NjhiMGFkMTlhYWMzNTgtMTcwMjcxNDczMg=='

def create_video():
    # Request headers
    url = 'https://api.heygen.com/v1/video.generate'
    headers = {
        'X-Api-Key': api_key,
        'Content-Type': 'application/json'
    }

    # Request data
    data = {
        "background": "#ffffff",
        "clips": [
            {
                "avatar_id": "Zoey-inTshirt-20220816",
                "avatar_style": "normal",
                "input_text": "hello there i am zoey and i am using a new voice",
                "offset": {
                    "x": 0,
                    "y": 0
                },
                "scale": 1,
                "voice_id": "ffdbe4de35d34391830da243f2b82e13"
            }
        ],
        "ratio": "16:9",
        "test": True,
        "version": "v1alpha"
    }

    # Make the POST request
    response = requests.post(url, json=data, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # The request was successful
        print("Request successful. Response data:", response.json())
    else:
        # The request failed
        print("Request failed. Status code:", response.status_code)


def get_video(video_id):

    url = f"https://api.heygen.com/v1/video_status.get?video_id={video_id}"

    headers = {
        "accept": "application/json",
        "x-api-key": api_key
    }
    response = requests.get(url, headers=headers)

    print(response.text)

# get_video()

def add_caption():
    url = "https://api.heygen.com/v1/video/caption.generate"

    payload = { "video_id": "85fa1df2a0dd48f5908781df11a63c2f" }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "x-api-key": api_key
    }

    response = requests.post(url, json=payload, headers=headers)

    print(response.text)

def get_caption():
    url = "https://api.heygen.com/v1/video/caption.get?video_id=85fa1df2a0dd48f5908781df11a63c2f"
    headers = {
        "accept": "application/json",
        "x-api-key": api_key
    }

    response = requests.get(url, headers=headers)

    print(response.text)


def list_avatars():

    # url = "https://api.heygen.com/v1/avatar.list"
    url = "https://api.heygen.com/v2/avatars"

    headers = {
        "accept": "application/json",
        "x-api-key": api_key
    }

    response = requests.get(url, headers=headers)

    print(response.text)


# list_avatars()
def list_voices():

    # url = "https://api.heygen.com/v1/voice.list"
    url = "https://api.heygen.com/v2/voices"

    headers = {
        "accept": "application/json",
        "x-api-key": api_key
    }

    response = requests.get(url, headers=headers)

    print(response.text)


def list_templates():
    url = "https://api.heygen.com/v2/templates"

    headers = {
        "accept": "application/json",
        "x-api-key": api_key
    }

    response = requests.get(url, headers=headers)

    print(response.text)

# create_video()
# get_video('cbf38fa4fc9e49abb5dd8c678d6ce385')
list_avatars()