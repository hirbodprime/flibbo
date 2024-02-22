import http.client
import base64
import os
import requests
from PIL import Image

api_key = "sk-Yf0mzTjul76HTCUGhMZzL8uOlzEDgGQryMYdnl0QrREoIYVw"

engine_id = "stable-diffusion-v1-6"
api_host = 'https://api.stability.ai'

if api_key is None:
    raise Exception("Missing Stability API key.")

def text_to_image(text):
    response = requests.post(
        f"{api_host}/v1/generation/{engine_id}/text-to-image",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}"
        },
        json={
            "text_prompts": [
                {
                    "text": f"{text}"
                }
            ],
            "cfg_scale": 7,
            "height": 1024,
            "width": 1024,
            "samples": 1,
            "steps": 30,
        },
    )

    if response.status_code != 200:
        raise Exception("Non-200 response: " + str(response.text))

    data = response.json()
    # Create the output directory if it doesn't exist
    output_dir = "./out"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Save the images
    for i, image in enumerate(data["artifacts"]):
        with open(f"{output_dir}/ai_stability_generated_image{i}.png", "wb") as f:
            f.write(base64.b64decode(image["base64"]))




def resize_image(image_path, output_size):
    with Image.open(image_path) as img:
        resized_img = img.resize(output_size)
        resized_img_path = image_path.split('.')[0] + '_resized.png'
        resized_img.save(resized_img_path)
        return resized_img_path

def image_to_video(image_path):
    # Resize the image to the required dimensions (e.g., 1024x576)
    resized_image_path = resize_image(image_path, (1024, 576))

    url = "https://api.stability.ai/v2alpha/generation/image-to-video"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }  # Removed the comma at the end

    # Open the resized image file in binary mode
    with open(resized_image_path, 'rb') as image_file:
        files = {
            'image': (resized_image_path, image_file, 'image/png'),
            'seed': (None, '0'),
            'cfg_scale': (None, '2.5'),
            'motion_bucket_id': (None, '40')
        }

        response = requests.post(url, files=files, headers=headers)

    # Check for response status and print the result
    if response.status_code == 200:
        print("Success:", response.text)
    else:
        print("Error:", response.text)





def get_video(video_id):
    conn = http.client.HTTPSConnection("api.stability.ai")

    headers = {
        'authorization': f"Bearer {api_key}",
    }

    conn.request("GET", f"/v2alpha/generation/image-to-video/result/{video_id}", headers=headers)

    res = conn.getresponse()
    data = res.read()

    # Check the content type of the response
    content_type = res.getheader('Content-Type')

    if 'video' in content_type:
        # If it's a video, write it to a file
        file_path = f'video_{video_id}.mp4'
        with open(file_path, 'wb') as file:
            file.write(data)
        print(f"Video saved to {file_path}")
    else:
        # If it's not a video, try to decode as text
        try:
            print(data.decode("utf-8"))
        except UnicodeDecodeError:
            print("Received data is not text and could not be decoded.")

# Replace 'your_api_key_here' and 'your_video_id_here' with your actual API key and video ID
video_id = '2cc064ebbcf9b9389de7f38dcf9165f9c10daa2545ec4fef66f74da8a7ddea6c'
# get_video(video_id)

image_path = 'chat_openai/image.png'
# image_to_video(image_path)


text_to_image('a dark shadow fighting the god of sun')