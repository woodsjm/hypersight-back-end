from flask import Blueprint, Flask, g, jsonify, request, session
from flask_bcrypt import check_password_hash, generate_password_hash
from flask_cors import CORS 

import bcrypt
import json
import os
import re
import sys
import urllib.parse

from routes.api import api
from routes.user import user


DEBUG = True
PORT = 8000

app = Flask(__name__)

app.secret_key = 'RLAKJDRANDOM STRING'

CORS(api, origins=['http://localhost:3000', 'https://hypersight.herokuapp.com'], supports_credentials=True)
CORS(app, origins=['http://localhost:3000', 'https://hypersight.herokuapp.com'], supports_credentials=True)
CORS(user, origins=['http://localhost:3000', 'https://hypersight.herokuapp.com'], supports_credentials=True)

app.register_blueprint(api)
app.register_blueprint(user)


@app.route('/') 
def index(): 
    return 'SERVER WORKING' 


if 'ON_HEROKU' in os.environ:
    print('hitting ')


if __name__ == '__main__':
    
    app.run(debug=DEBUG, port=PORT)