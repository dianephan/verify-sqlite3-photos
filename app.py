import os
from dotenv import load_dotenv
from flask import Flask, request, render_template, redirect, session, url_for
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from image_classifier import get_tags
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

# code for whatsapp portion here
def respond(message):
	response = MessagingResponse()
	response.message(message)
	return str(response)
	
@app.route('/', methods=['GET', 'POST'])
    return("gonna pause filepond for now and fdsafsfsdfsa my way...") 
    # return render_template('index.html')