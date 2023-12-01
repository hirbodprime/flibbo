import asyncio
import websockets
import json

async def test():
    uri = "ws://127.0.0.1:8000/ws/chat/"  # Adjust the URL as needed
    async with websockets.connect(uri) as websocket:
        # Constructing the message with sender and receiver details
        message_data = {
            "message": "Hello, hirbod! i am hirbod aflaki1",
            "sender": "hirbodaflaki",
            "receiver": "hirbod"  # Replace with the actual receiver's username
        }

        # Sending the message
        await websocket.send(json.dumps(message_data))

        # Waiting for a response and printing it
        response = await websocket.recv()
        print("Received:", response)

# Running the test function
asyncio.get_event_loop().run_until_complete(test())









# import asyncio
# import websockets
# import json
# import requests

# login_url = 'http://127.0.0.1:8000/account/api/token/'  # Adjust to your token auth URL
# credentials = {'email': 'hirbodprime@gmail.com', 'password': 'keyhan1234'}

# response = requests.post(login_url, data=credentials)

# # Debugging: Print the entire response to see what's being returned
# print("Response JSON:", response.json())

# # Extract the access token
# token = response.json().get('access')

# # Debugging: Print the token
# print("Extracted Token:", token)
# async def test():
#     uri = "ws://127.0.0.1:8000/ws/chat/"  # Adjust the URL as needed
#     headers = {'Authorization': f'Bearer {token}'}  # Set the authorization header

#     async with websockets.connect(uri, extra_headers=headers) as websocket:
#         # Constructing the message with sender and receiver details
#         message_data = {
#             "message": "Hello, hirbod! i am hirbod aflaki",
#             "sender": "hirbodaflaki",
#             "receiver": "hirbod"  # Replace with the actual receiver's username
#         }

#         # Sending the message
#         await websocket.send(json.dumps(message_data))

#         # Waiting for a response and printing it
#         response = await websocket.recv()
#         print("Received:", response)

# # Running the test function
# asyncio.get_event_loop().run_until_complete(test())

