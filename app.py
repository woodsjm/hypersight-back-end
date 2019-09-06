from flask import Flask, g, request, jsonify
from flask_pymongo import PyMongo 
from flask_cors import CORS
import json
import os
import datetime
import re





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
    print(data['csvfile'])
    print(data['filename'])
    result = coll.insert_many(data['csvfile'])

    # Dictionary for storing users chosen file name and the name of the collection (i.e. the
    # name of file as it is stored in MongoDB)
    file_name_reference = {data['filename']: logged_in_user}

    file_reference = mongo.db.users.update_one({
        'username': 'tom'
        }, {
        '$push': {'files': file_name_reference}
        })


    # print([r._id for r in result.inserted_ids])
    resultStr = str(result.inserted_ids)
    
    if (result.inserted_ids != None):
        return jsonify(data=resultStr, status={"code": 200, "message": "Success"})
    

@app.route("/prepdata", methods=["GET"])
def prepdata():
    
    result = mongo.db.list_collection_names()

    # Grab file name references from users collection
    file_name_references = mongo.db.users.find({
        'username': 'tom'
        }, {'files': 1})


    file_name_references_list = []
    for element in file_name_references:
        file_name_references_list.append(element['files'])


    flat_refs_list = [item for sublist in file_name_references_list for item in sublist]
    
    
    # Retrieve list of collections belonging to user
    array_of_user_collections = []
    for collection in result:
        if "tom" in collection:
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


@app.route('/delete', methods=["Delete"])
def delete_file():

    # Grab list of all collections
    all_files = mongo.db.list_collection_names()

    file_to_delete = "test_data"

    # Grab file name references from users collection
    file_name_references = mongo.db.users.find({
        'username': 'tom'
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




    print(file_name_references_list, "HERE IS THE LIST OF FILE NAME REFERENCES")

    return "working"


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