import requests
import json

BOT_TOKEN = "TEST_TOKEN" # We will use a fake token expected by our test
URL = f"https://mytelebot.com/telegram-webhook/"

payload = {
    "update_id": 10000,
    "message": {
        "message_id": 1365,
        "from": {
            "id": 1111111,
            "is_bot": False,
            "first_name": "Test User",
            "username": "testuser"
        },
        "chat": {
            "id": 1111111,
            "first_name": "Test User",
            "username": "testuser",
            "type": "private"
        },
        "date": 1441645532,
        "text": "/start"
    }
}

print(f"\n==========================================")
print(f"Testing Webhook URL: {URL}")
try:
    response = requests.post(URL, json=payload, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {response.headers}")
    with open("debug_404.html", "w", encoding="utf-8") as f:
        f.write(response.text)
    print("Saved response to debug_404.html")
    if response.status_code != 200:
        print("FAILED: Server returned an error.")
    else:
        print("SUCCESS: Webhook reached.")
except Exception as e:
    print(f"Error: {e}")
