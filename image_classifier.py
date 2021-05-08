import os
from dotenv import load_dotenv

from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_pb2, status_code_pb2

channel = ClarifaiChannel.get_grpc_channel()

# Note: You can also use a secure (encrypted) ClarifaiChannel.get_grpc_channel() however
# it is currently not possible to use it with the latest gRPC version

stub = service_pb2_grpc.V2Stub(channel)

# added flask stuff for debugging purpose
from flask import Flask, request
app = Flask(__name__)

load_dotenv()
CLARIFAI_API_KEY = os.environ.get('CLARIFAI_API_KEY')
metadata = (('authorization', CLARIFAI_API_KEY),)

def get_tags(image_url):
  print("[INFO] : image_url = ", image_url)
  request = service_pb2.PostModelOutputsRequest(
    model_id='aaa03c23b3724a16a56b629203edc62c',
    inputs=[
      resources_pb2.Input(data=resources_pb2.Data(image=resources_pb2.Image(url=image_url)))
  ])
  response = stub.PostModelOutputs(request, metadata=metadata)

  if response.status.code != status_code_pb2.SUCCESS:
    raise Exception("Request failed, status code: " + str(response.status.code))

  for concept in response.outputs[0].data.concepts:
    print('%12s: %.2f' % (concept.name, concept.value))
    
    
  # sky_tags = {}   # dictionary data structure for faster lookup time 
  # print("[INFO] : sky_tags = ", sky_tags)
  # for concept in response_data['outputs'][0]['data']['concepts']:
  #   sky_tags[concept['name']] = 1
  # return ("whatsgoignon")

def main():
  test_url = "https://raw.githubusercontent.com/dianephan/flask_upload_photos/main/UPLOADS/DRAW_THE_OWL_MEME.png"
  get_tags(test_url)

if __name__ == "__main__":
  main()
  