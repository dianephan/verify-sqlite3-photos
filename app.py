import os
from dotenv import load_dotenv
from flask import Flask, request, render_template, redirect, session, url_for
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
# from image_classifier import get_tags
from handle_blob_data import convert_into_binary, write_to_file, read_blob_data

import sqlite3
from sqlite3 import Error

load_dotenv()
app = Flask(__name__)
app.secret_key = 'dsfdgfdg;sd'

TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN= os.environ.get('TWILIO_AUTH_TOKEN')
VERIFY_SERVICE_SID= os.environ.get('VERIFY_SERVICE_SID')
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

app.config['UPLOAD_EXTENSIONS'] = ['jpg', 'png']

# code for whatsapp portion here
def respond(message):
  response = MessagingResponse()
  response.message(message)
  return str(response)

def send_verification(sender_phone_number):
  phone = sender_phone_number
  client.verify \
    .services(VERIFY_SERVICE_SID) \
    .verifications \
    .create(to=phone, channel='sms')
    
def check_verification_token(phone, token):
  check = client.verify \
    .services(VERIFY_SERVICE_SID) \
    .verification_checks \
    .create(to=phone, code=token)    
  return check.status == 'approved'

def allowed_file(filename):
  return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['UPLOAD_EXTENSIONS']
  # returns T/F if '.' in filename and the extension is parsed correctly 

# @app.route('/webhook', methods=['POST'])
# def reply():
#   sender_phone_number = request.form.get('From')
#   media_msg = request.form.get('NumMedia')    # 1 if its a picture 
#   latitude = request.values.get('Latitude')
#   longitude = request.values.get('Longitude')

#   try:
#     conn = sqlite3.connect('app.db')
#     print("Successful connection!")
#     cur = conn.cursor()
#     query = """SELECT EXISTS (SELECT 1 FROM uploads WHERE phone_number = (?))"""
#     cur.execute(query, [sender_phone_number])      
#     query_result = cur.fetchone()
#     user_exists = query_result[0]

#     # if user is not in the database and sends a word message such as "hello"
#     if user_exists == 0 and media_msg == '0' and latitude is None and longitude is None:
#       return respond(f'Please submit coordinates through the WhatsApp mobile app.')

#     # if the user is already in the database but sends a word message such as "hello"
#     elif user_exists == 1 and media_msg == '0':
#       return respond(f'Please send in a picture')

#     # if the user doesn't exist in the database yet and sends in their location data
#     elif user_exists == 0 and latitude and longitude:
#       insert_users = ''' INSERT INTO uploads(phone_number, latitude, longitude, file_name, file_blob)
#         VALUES(?,?,?,?,?) '''
#       cur = conn.cursor()
#       cur.execute(insert_users, (sender_phone_number, latitude, longitude, "PIC URL HERE", "BLOB UNNECESSARY",))
#       conn.commit()
#       return respond(f'Thanks for sending in your location! Finish your entry by sending in a photo of the sky.')
    
#     # if the user exists in the database and sends in a media message
#     elif user_exists == 1 and media_msg == '1':
#       pic_url = request.form.get('MediaUrl0')
#       look_up_user_query = """SELECT id FROM uploads WHERE phone_number = (?)"""
#       cur.execute(look_up_user_query, [sender_phone_number]) 
#       query_result = cur.fetchone()
#       user_id = query_result[0]
#       # need to check tags before adding to db
#       pic_url = request.form.get('MediaUrl0')  # URL of the person's media

#       # TO DO: CLARIFAI NOT WORKING WHYYY 
#       relevant_tags = get_tags(pic_url)
#       print("The tags for your picture are : ", relevant_tags)
#       if 'sky' in relevant_tags:
#         update_user_picture = '''UPDATE uploads
#           SET file_name = ?
#           WHERE user_id = ?'''
#         print("[DATA] : ")
#         cur = conn.cursor()
#         cur.execute(update_user_picture, (pic_url, user_id))
#         conn.commit()
#         print("[INFO] : sender has set their pic ")
#         return respond(f'You\'re all set!')
#       else:
#         return respond(f'Please send in a picture of the sky.')
#     else:
#       return respond(f'Please send your current location, then send a picture of the sky.')
#   except Error as e:
#     print(e)
#   finally:
#     if conn:
#       conn.close()
#     else:
#       error = "how tf did u get here."

# code for non-whatsapp users here
@app.route('/', methods=['GET', 'POST'])
def hello():
  return("gonna pause filepond for now and attempt my way...") 
  # return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
  if request.method == 'POST':
    print(request.form)
    sender_phone_number = request.form['formatted_number']
    latitude = request.form['latitude']
    longitude = request.form['longitude']
    print("[INFO] :", sender_phone_number, " sent in the coordinates - ", latitude, " ,", longitude)

    try:
      conn = sqlite3.connect('app.db')
      print("Successful connection!")
      cur = conn.cursor()
      query = """SELECT EXISTS (SELECT 1 FROM uploads WHERE phone_number = (?))"""
      cur.execute(query, [sender_phone_number])      
      query_result = cur.fetchone()
      user_exists = query_result[0]
      
      # if phone number not in db, add to db then send them to verify their acc
      if user_exists == 0: 
        session['sender_phone_number'] = sender_phone_number
        insert_users = ''' INSERT INTO uploads(phone_number, latitude, longitude, file_name, file_blob)
          VALUES(?,?,?,?,?) '''
        cur = conn.cursor()
        cur.execute(insert_users, (sender_phone_number, latitude, longitude, "PIC NAME HERE", "BLOB TBD",))
        conn.commit()
        print("[DATA] : successfully inserted into db")
        send_verification(session['sender_phone_number'])
        print("[INFO] : user needs to get their verification code now")
        return redirect(url_for('generate_verification_code'))

    # if phone number in db, send verification code
      if user_exists == 1: 
        session['sender_phone_number'] = sender_phone_number
        send_verification(sender_phone_number)
        print("[INFO] : user already exists so sending verification code now")
        return redirect(url_for('generate_verification_code'))
      return ("unsure lol????")
    except Error as e:
      print(e)
    finally:
      if conn:
        conn.close()
      else:
        error = "how tf did u get here."
  return render_template('register.html')
      
@app.route('/verifyme', methods=['GET', 'POST'])
def generate_verification_code():
  sender_phone_number = session['sender_phone_number']
  error = None
  if request.method == 'POST':
    verification_code = request.form['verificationcode']
    if check_verification_token(sender_phone_number, verification_code):
      # return render_template('uploadpage.html', username = username)
      return redirect(url_for('upload_file'))
    else:
      error = "Invalid verification code. Please try again."
      return render_template('verifypage.html', error = error)
  return render_template('verifypage.html')

@app.route('/upload')
def upload_file():
  return render_template('uploadpage.html')

@app.route('/uploader', methods = ['GET', 'POST'])
def submitted_file():
  sender_phone_number = session['sender_phone_number']
  if request.method == 'POST':
    f = request.files['file']
    if f and allowed_file(f.filename):
      user_secure_filename = secure_filename(f.filename)
      print("[INFO] : user_secure_filename = ", user_secure_filename)
      
      try:
        conn = sqlite3.connect('app.db')
        print("Successful connection!")
        cur = conn.cursor()
        look_up_user_query = """SELECT id FROM uploads WHERE phone_number = (?)"""
        cur.execute(look_up_user_query, [sender_phone_number]) 
        query_result = cur.fetchone()
        user_id = query_result[0]
        # need to check tags before adding to db

        # # TO DO: CLARIFAI NOT WORKING WHYYY 
        # relevant_tags = get_tags(pic_url)
        # print("The tags for your picture are : ", relevant_tags)
        # if 'sky' in relevant_tags:
        update_user_picture = '''UPDATE uploads
          SET file_name = ?
          WHERE id = ?'''
        cur = conn.cursor()
        cur.execute(update_user_picture, (user_secure_filename, user_id))
        conn.commit()
        print("[INFO] : sender has set their pic ")
        return render_template('success.html')
      except Error as e:
        print(e)
      finally:
        if conn:
          conn.close()
        else:
          error = "how tf did u get here."
    else:
      error = "Please upload a valid file."
      return render_template('uploadpage.html', error = error)
    
    


