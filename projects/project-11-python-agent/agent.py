import os
from dotenv import load_dotenv
from requests import post
from openai import OpenAI

if __name__ == "__main__":
    load_dotenv()

    DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
    if not DEEPSEEK_API_KEY:
        print("DEEPSEEK_API_KEY is not found")
    else:
        print("DEEPSEEK_API_KEY is found")

    response = post(
        "https://api.deepseek.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "deepseek-v4-flash",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": "Hello"},
            ],
            "stream": False,
            "reasoning_effort": "medium",
            "extra_body": {"thinking": {"type": "enabled"}}
        }
    )
    if response.status_code != 200:
        print(f"Request failed with status code: {response.status_code}")
        print(f"Response: {response.message}")
    else:
        print(response.json().get("choices")[0].get("message").get("content"))  #choices[0].message.content

    # client = OpenAI(
    #     api_key=DEEPSEEK_API_KEY,
    #     base_url="https://api.deepseek.com")
    
    # response = client.chat.completions.create(
    # model="deepseek-v4-flash",
    # messages=[
    #     {"role": "system", "content": "You are a helpful assistant"},
    #     {"role": "user", "content": "Hello"},
    # ],
    # stream=False,
    # reasoning_effort="medium",
    # extra_body={"thinking": {"type": "enabled"}}
    # )

    # print(response.choices[0].message.content)

    



