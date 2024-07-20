import json


def convertDictToJasonFile(dict, path):
    with open(path, 'w', encoding='utf-8') as json_file:
        json.dump(dict, json_file, indent=4)


def createHeaderFileFromDict(dict, path):
    # create a list of dict
    classes = []
    for Class in dict:
        classes.append(Class)

    # create txt document with list of dict
    with open(path, 'w', encoding='utf-8') as file:
        for Class in classes:
            file.write(f"{Class}\n")


def getJson(path):
    with open(path, 'r', encoding='utf-8') as file:
        jsonFile = json.load(file)
    return jsonFile
