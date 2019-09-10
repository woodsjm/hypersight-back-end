from flask import Flask, g, request, session, jsonify
from flask_pymongo import PyMongo 
from flask_cors import CORS
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user, login_required 
from pymongo import MongoClient
import bcrypt
import json
import os
import datetime
import re
import sys


DEBUG = True
PORT = 8000


# ----------------DB SETUP----------------
MONGO_URL = os.environ.get('MONGO_URL')
if not MONGO_URL:
    MONGO_URL = "mongodb://localhost:27017/hypersight"

app = Flask(__name__)
# app.config["MONGO_URI"] = "mongodb://localhost:27017/hypersight"
app.config['MONGO_URI'] = MONGO_URL



mongo = PyMongo(app)

app.secret_key = 'RLAKJDRANDOMASDFLKENCASDFWERACSVNASDFLKJQWEFASDF STRING'

CORS(app, origins=['http://localhost:3000', 'https://hypersight.herokuapp.com'], supports_credentials=True)

# # ----------------RETURN APPROPRIATE HEADERS ON EVERY REQUEST TO SERVER----------------
# @app.after_request
# def add_cors(resp):
    
#     resp.headers['Access-Control-Allow-Origin'] = flask.request.headers.get('Origin','*')
#     resp.headers['Access-Control-Allow-Credentials'] = 'true'
#     resp.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS, GET'
#     resp.headers['Access-Control-Allow-Headers'] = flask.request.headers.get( 
#         'Access-Control-Request-Headers', 'Authorization' )
    
#     if app.debug:
#         resp.headers['Access-Control-Max-Age'] = '1'

#     return resp



# ----------------LOG USER IN----------------
@app.route('/login', methods=["POST"])
def login():
    data = request.get_json()

    login_user = mongo.db.users.find_one({'username': data['username']})

    if login_user:

        if bcrypt.hashpw(data['password'].encode('utf-8'), login_user['password'].encode('utf-8')) == login_user['password'].encode('utf-8'):
            session['username'] = data['username']
            return jsonify(data={}, status={"code": 200, "message": "Successfully logged in"})
    
        return jsonify(data={}, status={"code": 401, "message": "Invalid Username/Password"})



# ----------------LOG USER OUT----------------
@app.route('/logout', methods=["POST"])
def logout():

    session.pop('username', None)
  
    return jsonify(data={}, status={"code": 200, "message": "User successfully logged out"})   



# ----------------REGISTER NEW USER----------------
@app.route("/register", methods=["POST"])
def register():

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

    

# ----------------ADD FILE----------------
@app.route("/upload", methods=["POST"])
def upload_csv():
    
    # GET CURRENT DATE AND TIME AS STRING
    date_and_time = str(datetime.datetime.now())
    
    # STRIP THE CURRENT DATE AND TIME STRING
    datetime_stripped = re.sub('[-: .]', '', date_and_time)
    
    the_current_user = session['username']

    logged_in_user = the_current_user + datetime_stripped
    coll = mongo.db.create_collection(logged_in_user)

    data = request.get_json()
    result = coll.insert_many(data['csvfile'])

    # Dictionary for storing users chosen file name and the name of the collection (i.e. the
    # name of file as it is stored in MongoDB)
    file_name_reference = {data['filename']: logged_in_user}

    the_current_user = session['username']

    file_reference = mongo.db.users.update_one({
        'username': the_current_user
        }, {
        '$push': {'files': file_name_reference}
        })

    resultStr = str(result.inserted_ids)
    
    if (result.inserted_ids != None):
        return jsonify(data=resultStr, status={"code": 200, "message": "Success"})
    


# ----------------LIST ALL FILES----------------
@app.route("/prepdata", methods=["GET"])
def prepdata():
    
    result = mongo.db.list_collection_names()

    the_current_user = session['username']

    # Grab file name references from users collection
    file_name_references = mongo.db.users.find({
        'username': the_current_user
        }, {'files': 1})

    file_name_references_list = []
    for element in file_name_references:
        file_name_references_list.append(element['files'])

    flat_refs_list = [item for sublist in file_name_references_list for item in sublist]


    
    # Retrieve list of collections belonging to user
    array_of_user_collections = []
    for collection in result:
        if the_current_user in collection:
            array_of_user_collections.append(collection)
    
    # Construct an individual file by creating a list with all documents from a collection. 
    # Then create a list of such files, making each individual file the value of a key - in a dictionary -
    # whose name is linked to the collection name. 
    user_files = []
    for collection in array_of_user_collections:

        file = mongo.db[collection].find()

        built_file = []
        for document in file:
            document['_id'] = str(document['_id'])
            built_file.append(document)

        for file in built_file:
            if "_id" in file:
                del file["_id"]

        for file_name_ref in flat_refs_list:
            for key, value in file_name_ref.items():
                if value == collection:
                    user_file = {key: built_file}
                    user_files.append(user_file)
    
    
    return jsonify(data=user_files, status={"code": 200, "message": "Success"})



# ----------------DELETE FILE----------------
@app.route('/delete/<filename>', methods=["Delete"])
def delete_file(filename):

    the_current_user = session['username']

    # Grab list of all collections
    all_files = mongo.db.list_collection_names()

    file_to_delete = filename

    # Grab file name references from users collection
    file_name_references = mongo.db.users.find({
        'username': the_current_user
        }, {'files': 1})

    # Convert file name references into a list
    file_name_references_list = []
    for element in file_name_references:
        file_name_references_list.append(element['files'])

    # Find the name of the collection matching the given file name
    for file_name in file_name_references_list[0]:
        file_reference = [*file_name]
        if file_to_delete == file_reference[0]:
            # The collection that will be deleted
            collection_to_delete = file_name[file_to_delete]
            mongo.db.drop_collection(collection_to_delete)

    return jsonify(data='resources successfully deleted', status={"code": 200, "message": "Resource deleted"})



# ----------------UPDATE FILE NAME----------------
@app.route('/edit/<filename>', methods=["PUT"])
def edit_file(filename):

    the_current_user = session['username']

    data = request.get_json()

    new_filename = data
    
    file_name_references = mongo.db.users.find({
        'username': the_current_user
        }, {'files': 1})

    # Grab file name references from users collection
    file_name_references_list = []
    for element in file_name_references:
        file_name_references_list.append(element['files'])

    for file_ref in file_name_references_list[0]:
        file_ref_key = [*file_ref]
        if filename == file_ref_key[0]:

            file_reference_value = file_ref[file_ref_key[0]]

            delete_file_ref = mongo.db.users.update_one({
                    'username': the_current_user
                    }, {
                    '$pull': {'files': {file_ref_key[0]: file_reference_value}}
                    })

            add_file_ref = mongo.db.users.update_one({
                    'username': the_current_user
                    }, {
                    '$push': {'files': {new_filename: file_reference_value}}
                    }) 
        
    return jsonify(data='resource successfully updated', status={"code": 200, "message": "Resource updated"})



@app.route('/') 
def index(): 
    return 'SERVER WORKING' 

if 'ON_HEROKU' in os.environ:

    print('hitting ')

if __name__ == '__main__':
    
    app.run(debug=DEBUG, port=PORT)