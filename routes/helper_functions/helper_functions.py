# -------------------------------------------
#               Helper Functions
# -------------------------------------------

def get_file_name_references(current_user):
    file_name_references = mongo.db.users.find({
        'username': current_user
        }, {'files': 1})
    return file_name_references

def make_file_name_references_list(file_refs):
    file_name_references_list = []
    for element in file_refs:
        file_name_references_list.append(element['files'])
    return file_name_references_list