import requests

api_key = "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"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "OpenAI-Beta": "assistants=v1"  # Include this header
}

data = {
    "model": "gpt-3.5-turbo",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What's the weather like today?"}
    ]
}

response = requests.post("https://api.openai.com/v1/threads", json=data, headers=headers)

if response.status_code == 200:
    thread_id = response.json()["id"]
    print(f"Thread ID: {thread_id}")
    # You can continue the conversation by using the thread_id
else:
    print(f"Error: {response.status_code} - {response.text}")
