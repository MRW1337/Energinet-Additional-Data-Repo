"""
Module Name: getCgmProfilesFromFolder
Author: Magnus Rasmussen
Mail: MRW@energinet.dk
Date: 2024-16-07
Version: 1.0

Arguments:
    - Path: str
    - cgmClasses: dict

Returns:
    - cgmClasses: dict (3 level nested dictionary)

Methods:
    public
     - getEquipmentProfiles(directoryPath)
        private
        - _parseXML(path)(private)

Description:
This script uses a recursive function to get all files in a directory specified by argument path
and parse the XML files. The script then creates a dictionary structure with the following format:

    cgmClasses = {
        'Line': {
            'object_mrid1': {
                'attribute1': 'value1',
                'attribute2': 'value2',
            },
            'object_mrid2': {
                'attribute1': 'value1',
            },
        },
        'GeographicalRegion': {
            'object_mrid3': {
                'attribute1': 'value1',
                'attribute2': 'value2',
            },
            'object_mrid4': {
                'attribute1': 'value1',
            },
        },
        # ... more categories
    }

Usage:
    Convert a CGMES profile to a usable datastructure for further dataprocessing

Condition:
    CGMES Profile has to adhere to NC 2.3 Standard for modelling of electrical systems
    in an XML format.

Dependencies:
    None

Notes:
- Ensure that the dictionary keys are correctly structured as described.
"""

import xml.etree.ElementTree as ET
import os


# Recursive function to get all files in a directory
def getCgmProfilesFromFolder(directoryPath):
    # Direcetory path to proces from
    Profiles = []
    for file in os.listdir(directoryPath):
        filePath = os.path.join(directoryPath, file)
        if os.path.isfile(filePath) and filePath.endswith('.xml'):
            Profiles.append(filePath)
        else:
            print('Skipping file since its of type xml: ' + filePath)
    print('Getting EQ Profiles from:' + '\n' + str('\n'.join(Profiles)))

    # Define output
    cgmClasses = {}

    # Parse the XML files
    for profile in Profiles:
        classes = _parseXML(profile)
        cgmClasses[profile.split('\\')[-1]] = classes

    return cgmClasses


# function to parse xml files approprietly
def _parseXML(path):

    print('Parsing XML: ' + path.split('\\')[-1])
    with open(path, "r", encoding="utf-8") as file:
        root = ET.parse(file).getroot()

    cgmClasses = {}
    # Loop through all first-level objects
    for element in root:
        objectCategory = _stripNamespace(element.tag)

        # Check if the object is an existing class
        if objectCategory not in cgmClasses:
            cgmClasses[objectCategory] = {}

        # loop through attribute of first-level object. this is just the object mrid
        for objectName, objectmRID in element.attrib.items():
            objectmRID = _removePrefixFromMrid(_stripNamespace(objectmRID))

            # Check if the objectmRID is an existing object under the class
            if objectmRID not in cgmClasses[objectCategory]:
                cgmClasses[objectCategory][objectmRID] = {}

        # Loop through attributes of the object
        for objectAttributes in element:

            # Add reference to other objects
            for namespace, attrValue in objectAttributes.attrib.items():
                objectReferenceName = _stripNamespace(objectAttributes.tag)
                objectAttributeValue = _removePrefixFromMrid(attrValue)

                # Check if the reference is an existing reference
                if objectReferenceName not in cgmClasses[objectCategory][objectmRID]:
                    cgmClasses[objectCategory][objectmRID][objectReferenceName] = objectAttributeValue

            # Add text attributes
            if objectAttributes.text and objectAttributes.text.strip():
                objectAttributeName = _stripNamespace(objectAttributes.tag)
                objectAttributeValue = _removePrefixFromMrid(objectAttributes.text.strip())

                # Check if text attribute is an existing attribute
                if objectAttributeName not in cgmClasses[objectCategory][objectmRID]:
                    cgmClasses[objectCategory][objectmRID][objectAttributeName] = objectAttributeValue

    return cgmClasses


def _removePrefixFromMrid(mrid):
    if mrid[0] == '#':
        mrid = mrid[1:]
    if mrid[0] == '_':
        mrid = mrid[1:]

    return mrid


# Function to strip namespace
def _stripNamespace(tag):
    return tag.split('}', 1)[1] if '}' in tag else tag
