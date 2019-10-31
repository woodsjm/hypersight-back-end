from flask import Blueprint, jsonify, request, session

import datetime
import os
import re
import sys

from routes.helper.helper_function import  helper_function

api = Blueprint('api', 'api', url_prefix='/api')


# ----------------ADD FILE----------------
@api.route("/upload", methods=["POST"])
def upload_csv():
    
    from database import mongo

    date_and_time = str(datetime.datetime.now())

    # Dynamic string for naming each collection (i.e. CSV file)
    datetime_stripped = re.sub('[-: .]', '', date_and_time)
    
    current_user = session['username']

    logged_in_user = current_user + datetime_stripped
    coll = mongo.db.create_collection(logged_in_user)

    data = request.get_json()
    result = coll.insert_many(data['csvfile'])

    # Store users chosen file name and the name of the collection (i.e. the
    # name of file as it is stored in MongoDB)
    file_name_reference = {data['filename']: logged_in_user}

    file_reference = mongo.db.users.update_one({
        'username': current_user
        }, {
        '$push': {'files': file_name_reference}
        })

    resultStr = str(result.inserted_ids)
    
    if (result.inserted_ids != None):
        return jsonify(data=resultStr, status={"code": 200, "message": "Success"})
    

# ----------------LIST ALL FILES----------------
@api.route("/prepdata", methods=["GET"])
def prepdata():
    
    from database import mongo

    result = mongo.db.list_collection_names()

    current_user = session['username']

    hf = helper_function(current_user)

    flat_refs_list = [item for sublist in hf for item in sublist]
    
    array_of_user_collections = []
    for collection in result:
        if current_user in collection:
            array_of_user_collections.append(collection)
    
    user_files = []
    #Reconstruct individual CSV files
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
@api.route('/delete/<filename>', methods=["Delete"])
def delete_file(filename):

    from database import mongo

    current_user = session['username']

    all_files = mongo.db.list_collection_names()

    file_to_delete = filename

    hf = helper_function(current_user)

    for file_name in hf[0]:
        file_reference = [*file_name]
        if file_to_delete == file_reference[0]:
            # The collection that will be deleted
            collection_to_delete = file_name[file_to_delete]
            mongo.db.drop_collection(collection_to_delete)

    return jsonify(data='resources successfully deleted', status={"code": 200, "message": "Resource deleted"})


# ----------------UPDATE FILE NAME----------------
@api.route('/edit/<filename>', methods=["PUT"])
def edit_file(filename):

    from database import mongo

    current_user = session['username']

    data = request.get_json()

    new_filename = data

    hf = helper_function(current_user)

    for file_ref in hf[0]:
        file_ref_key = [*file_ref]
        if filename == file_ref_key[0]:

            file_reference_value = file_ref[file_ref_key[0]]

            delete_file_ref = mongo.db.users.update_one({
                    'username': current_user
                    }, {
                    '$pull': {'files': {file_ref_key[0]: file_reference_value}}
                    })

            add_file_ref = mongo.db.users.update_one({
                    'username': current_user
                    }, {
                    '$push': {'files': {new_filename: file_reference_value}}
                    }) 
        
    return jsonify(data='resource successfully updated', status={"code": 200, "message": "Resource updated"})

