import os
import sys

# ----------------Helper Function--------------------
def helper_function(current_user):

    from database import mongo

    file_name_references = mongo.db.users.find({
        'username': current_user
        }, {'files': 1})

    file_name_references_list = []
    for element in file_name_references:
        file_name_references_list.append(element['files'])

    return file_name_references_list





