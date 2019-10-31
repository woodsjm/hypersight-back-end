from flask_pymongo import PyMongo 
from pymongo import MongoClient

import os
import urllib.parse

import webapp


# Heroku Credentials
username = os.environ.get('DATABASE_USERNAME')
password = os.environ.get('DATABASE_PASSWORD')

if not username and not password:
    # Local Config
    MONGO_URL = "mongodb://localhost:27017/hypersight"
    webapp.app.config['MONGO_URI'] = MONGO_URL
    mongo = PyMongo(webapp.app)
else:
    # Heroku Config
    escaped_username = urllib.parse.quote_plus(username)
    escaped_password = urllib.parse.quote_plus(password)

    connection_string = os.environ.get('DATABASE_CONNECTION_STRING')

    MONGO_URL = 'mongodb://' + escaped_username + ':' + escaped_password + connection_string
    mongo = MongoClient(MONGO_URL)


