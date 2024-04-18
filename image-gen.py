from openai import OpenAI
from dotenv import load_dotenv
from os import environ
from time import sleep
load_dotenv()

client = OpenAI(api_key=environ.get("OPEN_API_KEY"))

prompt = input("prompt: ")
while True:
  response = client.images.generate(
    model="dall-e-3",
    prompt=prompt,
    size="1792x1024",
    quality="hd",
    n=1,
  )

  image_url = response.data[0].url
  print(image_url)
  sleep(10)
