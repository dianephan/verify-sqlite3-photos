import os
from clarifai.rest import ClarifaiApp
from dotenv import load_dotenv
load_dotenv()

CLARIFAI_API_KEY = os.environ.get('CLARIFAI_API_KEY')

app = ClarifaiApp(api_key=CLARIFAI_API_KEY)

def get_tags(image_url):
  response_data = app.tag_urls([image_url])
  sky_tags = {}   # dictionary data structure for faster lookup time 
  for concept in response_data['outputs'][0]['data']['concepts']:
    sky_tags[concept['name']] = 1
  return sky_tags