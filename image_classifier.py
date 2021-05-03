import os
from clarifai.rest import ClarifaiApp
from dotenv import load_dotenv
load_dotenv()

CLARIFAI_API_KEY = os.environ.get('CLARIFAI_API_KEY')

app = ClarifaiApp(api_key=CLARIFAI_API_KEY)

def get_tags(image_url):
  test_url = "https://slack-imgs.com/?c=1&o1=ro&url=https%3A%2F%2Fpbs.twimg.com%2Fmedia%2FE0K1YVeVoAMFOXm.jpg"
  print("[INFO] : test_url = ", test_url)

  # # response_data = app.tag_urls([image_url])
  # response_data = app.tag_urls([test_url])
  # print("[INFO] : response_data = ", response_data)
  # sky_tags = {}   # dictionary data structure for faster lookup time 
  # print("[INFO] : sky_tags = ", sky_tags)
  # for concept in response_data['outputs'][0]['data']['concepts']:
  #   sky_tags[concept['name']] = 1
  return ("whatsgoignon")