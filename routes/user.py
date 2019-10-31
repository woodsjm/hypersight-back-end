from flask import Blueprint, jsonify, request, session
from flask_bcrypt import generate_password_hash, check_password_hash

import bcrypt
import os
import sys

from routes.helper.helper_function import  helper_function

user = Blueprint('user', 'user', url_prefix='/user')


# ----------------LOG IN--------------------
@user.route('/login', methods=["POST"])
def login():

    from database import mongo 

    data = request.get_json()

    login_user = mongo.db.users.find_one({'username': data['username']})

    if login_user:

        if bcrypt.hashpw(data['password'].encode('utf-8'), login_user['password'].encode('utf-8')) == login_user['password'].encode('utf-8'):
            session['username'] = data['username']
            return jsonify(data={}, status={"code": 200, "message": "Successfully logged in"})
    
        return jsonify(data={}, status={"code": 401, "message": "Invalid Username/Password"})


# ----------------LOG OUT--------------------
@user.route('/logout', methods=["POST"])
def logout():

    session.pop('username', None)
  
    return jsonify(data={}, status={"code": 200, "message": "User successfully logged out"})   


# ----------------REGISTER----------------
@user.route("/register", methods=["POST"])
def register():

    from database import mongo

    data = request.get_json()

    user_exists = mongo.db.users.find({'username': data['username']})

    user_response = []
    
    for item in user_exists:
        user_response.append(item)

    try:

        if user_response:

            return jsonify(data={}, status={"code": 401, "message": "A user with that name exists"})

            
        elif not user_response:
            
            hashed_password = generate_password_hash(data['password']).decode('utf8')

            user = mongo.db.users.insert_one({
                'username': data['username'],
                'email': data['email'],
                'password': hashed_password,
                'files': []
                })

            session['username'] = data['username']

            return jsonify(data={}, status={'code': 200, "message": "Success"})


    except: 
        return jsonify(data={}, status={"code": 401, "message": "Registration failed"})
  