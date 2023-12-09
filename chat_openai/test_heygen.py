import requests
import json

# URL of the API endpoint
url = 'https://api.heygen.com/v1/video.generate'

# Your API key
api_key = 'MDk4MWQ0ZTU1YzA1NDFhYWJmMmYyZjhhOGQ5MmRmMjAtMTcwMTc2OTI1NA=='

# Headers for the request
headers = {
    'X-Api-Key': api_key,
    'Content-Type': 'application/json'
}

# Data payload for the POST request
data = {
    "background": "#ffffff",
    "clips": [
        {
            "avatar_id": "Daisy-inskirt-20220818",
            "avatar_style": "normal",
            "input_text": "My name is Ahmad Abdolahi I am from iran and i like dod, so lets go and take a dod",
            "offset": {
                "x": 0,
                "y": 0
            },
            "scale": 1,
            "voice_id": "1bd001e7e50f421d891986aad5158bc8"
        }
    ],
    "ratio": "16:9",
    "test": True,
    "version": "v1alpha"
}

# Making the POST request
response = requests.post(url, headers=headers, data=json.dumps(data))

# Printing the response
print(response.status_code)
print(response.text)
