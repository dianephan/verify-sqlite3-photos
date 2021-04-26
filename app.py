import os
from dotenv import load_dotenv
from flask import Flask, request, render_template, redirect, session, url_for
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from image_classifier import get_tags

import sqlite3
from sqlite3 import Error

load_dotenv()
app = Flask(__name__)
app.secret_key = 'dsfdgfdg;sd'

TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN= os.environ.get('TWILIO_AUTH_TOKEN')
VERIFY_SERVICE_SID= os.environ.get('VERIFY_SERVICE_SID')
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# code for whatsapp portion here
def respond(message):
  response = MessagingResponse()
  response.message(message)
  return str(response)

@app.route('/webhook', methods=['POST'])
def reply():
  sender_phone_number = request.form.get('From')
  media_msg = request.form.get('NumMedia')    # 1 if its a picture 
  message_latitude = request.values.get('Latitude')
  message_longitude = request.values.get('Longitude')

  try:
    conn = sqlite3.connect('app.db')
    print("Successful connection!")
    cur = conn.cursor()
    query = """SELECT EXISTS (SELECT 1 FROM uploads WHERE phone_number = (?))"""
    cur.execute(query, [sender_phone_number])      
    query_result = cur.fetchone()
    user_exists = query_result[0]

    # if user is not in the database and sends a word message such as "hello"
    if user_exists == 0 and media_msg == '0' and message_latitude is None and message_longitude is None:
      return respond(f'Please submit coordinates through the WhatsApp mobile app.')

    # if the user is already in the database but sends a word message such as "hello"
    elif user_exists == 1 and media_msg == '0':
      return respond(f'Please send in a picture')

    # if the user doesn't exist in the database yet and sends in their location data
    elif user_exists == 0 and message_latitude and message_longitude:
      insert_users = ''' INSERT INTO uploads(phone_number, latitude, longitude, file_name, file_blob)
        VALUES(?) '''
      cur = conn.cursor()
      cur.execute(insert_users, (sender_phone_number, message_latitude, message_longitude, "UPDATEPIC", "UPDATEBLOB",))
      conn.commit()
      return respond(f'Thanks for sending in your location! Finish your entry by sending in a photo of the sky.')
    # if the user exists in the database and sends in a media message
    elif user_exists == 1 and media_msg == '1':
      pic_url = request.form.get('MediaUrl0')
      look_up_user_query = """SELECT id FROM uploads WHERE phone_number = (?)"""
      cur.execute(look_up_user_query, [sender_phone_number]) 
      query_result = cur.fetchone()
      user_id = query_result[0]
      # need function to create blob data here


      update_user_picture = '''UPDATE uploads
        SET file_name = ?
        SET file_name, file_blob = ?
        WHERE user_id = ?'''
      cur = conn.cursor()
      cur.execute(update_user_picture, (pic_url, user_id))
      conn.commit()
      return respond(f'You\'re all set!')





  # ???????
  if media_msg == '1' and sender in sky_pics:
    pic_url = request.form.get('MediaUrl0')  # URL of the person's media
    relevant_tags = get_tags(pic_url)
    print("The tags for your picture are : ", relevant_tags)
    # if 'sky' or 'weather' in relevant_tags and sky_pics.get(sender)[4] is None:
    if 'sky' in relevant_tags:


      sky_pics.get(sender)[4] = pic_url
      print("[INFO] : sender has set their pic " , sky_pics.get(sender))
      return respond(f'Thanks for sending in a picture.')
      # if 'sky' or 'weather' in relevant_tags and sky_pics.get(sender)[4] is not None:
      #     # replace the picture URL in sky_pics dictionary
      #     sky_pics.get(sender)[4] = pic_url
      #     print("[INFO] : sender has updated their pic " , sky_pics.get(sender))
      #     return respond(f'Your picture has been updated.')
      else:
        return respond(f'Please send in a picture of the sky.')
  elif message_latitude is not None and message_longitude is not None:
    location = get_location(message_latitude, message_longitude)
    sky_pics[sender] = [None] * 5
    sky_pics.get(sender)[0] = message_latitude
    sky_pics.get(sender)[1] = message_longitude
    sky_pics.get(sender)[2] = location[0]
    sky_pics.get(sender)[3] = location[1]
    return respond(f'Your location has been set to : {location}')
  else:
    return respond(f'Please send your current location, then send a picture of the sky.')

# code for non-whatsapp users here
@app.route('/', methods=['GET', 'POST'])
  return "empty for now"

@app.route('/register', methods=['GET', 'POST'])
def register():
   if request.method == 'POST':
      phone_number = request.form['phone']
      latitude = request.form['latitude']
      longitude = request.form['longitude']
      print("[INFO] : ")
      return render_template('register.html')
   return render_template('index.html')
