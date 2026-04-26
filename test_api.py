import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client()

prompt = "Hello"
for model_name in ["gemini-1.5-flash", "gemini-1.5-flash-8b", "gemini-1.5-pro", "gemini-2.5-flash"]:
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
        )
        print(f"Success with {model_name}")
    except Exception as e:
        print(f"Failed with {model_name}: {e}")
