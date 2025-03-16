import os
import requests
import json

def lambda_handler(event, context):
  url = "https://api.line.me/v2/bot/message/push"

  payload = json.dumps({
    "to": "{}".format(os.environ["RECIPIENT_ID"]),
    "messages": [
      {
        "type": "text",
        "text": "Hello, world1"
      },
      {
        "type": "text",
        "text": "Hello, world2"
      }
    ]
  })

  headers = {
    'Content-Type': 'application/json',
    'Authorization': "Bearer {}".format(os.environ["LINE_CHANNEL_ACCESS_TOKEN"])
  }

  response = requests.request("POST", url, headers=headers, data=payload)

  print(response.text)
