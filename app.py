from flask import Flask, g, request, jsonify
from flask_pymongo import PyMongo 
from flask_cors import CORS
import json
import os
import datetime
import re
from bson import Binary, Code 
from bson.json_util import dumps




DEBUG = True
PORT = 8000


app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/employees"
mongo = PyMongo(app)

#app.register_blueprint(api)

CORS(app, origins=['http://localhost:3000'], supports_credentials=True)

@app.route("/upload", methods=["POST"])
def upload_csv():
    print("*******************")
    print("INSIDE UPLOAD_CSV")
    
    
    # GET CURRENT DATE AND TIME AS STRING
    date_and_time = str(datetime.datetime.now())
    print(date_and_time)

    # STRIP THE CURRENT DATE AND TIME STRING
    datetime_stripped = re.sub('[-: .]', '', date_and_time)
    print(datetime_stripped)
    logged_in_user = "tom" + datetime_stripped
    coll = mongo.db.create_collection(logged_in_user)

    data = request.get_json()
    print(data)
    result = coll.insert_many(data)


    # print([r._id for r in result.inserted_ids])
    resultStr = str(result.inserted_ids)
    
    if (result.inserted_ids != None):
        return jsonify(data=resultStr, status={"code": 200, "message": "Success"})

@app.route("/prepdata", methods=["GET"])
def prepdata():
    
    result = mongo.db.list_collection_names()
    

    # Retrieve list of collections belonging to user
    array_of_user_collections = []
    for collection in result:
        if "tom" in collection:
            array_of_user_collections.append(collection)
    print(array_of_user_collections)

    # Construct an individual file by creating a list with all documents from a collection, and 
    # then create a list of such files.
    user_files = []
    for collection in array_of_user_collections:
        file = mongo.db[collection].find()
        built_file = []
        for document in file:
            built_file.append(document)
        user_files.append(built_file)

    # Convert ObjectIds to strings
    jsonifiable_user_files = []
    for file in user_files:
        jsonifiable_built_file = []
        for document in file:
            document['_id'] = str(document['_id'])
            jsonifiable_built_file.append(document)
        jsonifiable_user_files.append(jsonifiable_built_file)

    return jsonify(data=jsonifiable_user_files, status={"code": 200, "message": "Success"})
    # desired_collection = mongo.db[coll].find()
    # for document in desired_collection:
    #     print(document)
    #return jsonify(data=user_files, status={"code": 200, "message": "Success"})



# @app.route("/<username>")
# def user_profile(username):
#     user = mongo.db.users.find_one({"username": username})
#     print(user["username"])
#     print(user["_id"])
#     userid = str(user["_id"])
#     return userid

@app.route('/') 
def index(): 
    return 'SERVER WORKING' 


if __name__ == '__main__':
    
    app.run(debug=DEBUG, port=PORT)