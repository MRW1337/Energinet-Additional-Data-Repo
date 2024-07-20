import sys
import os
from contingencyMethods import buildcontingencyEquipmentList, createContingencyProfile
from fileHandlingMethods import getCgmProfilesFromFolder, convertDictToJasonFile, createHeaderFileFromDict, getJson


def main(inputArgs):
    try:
        print('Input Arguments:')
        for keys in inputArgs.keys():
            print(keys + ' : ' + str(inputArgs[keys]))
    except Exception as e:
        print('Error in input arguments error: ' + str(e))
        sys.exit()

    # Get all Equipment from the Equipment Profile
    try:
        cgmClasses = getCgmProfilesFromFolder(inputArgs['directoryPath'])
        convertDictToJasonFile(cgmClasses, pathToCgmClasses)
        createHeaderFileFromDict(cgmClasses, pathToCgmHeader)
    except Exception as e:
        print(str(e))

    # Get JSON database for currently defined ordinary contingencies
    contingencies = getJson(pathToContingencies)

    # Create reverse dictionary(sort of) for quick lookup and comparison with potential new contingencies. key is equipmentMrid and value is contingencyEquipmentMrid
    existingContingencies = {}
    for key in contingencies['ContingencyEquipment'].keys():
        equipmentMrid = contingencies['ContingencyEquipment'][key]['ContingencyEquipment.Equipment']
        existingContingencies[equipmentMrid] = key

    # Create dictionary of equipment to create contingencies on
    eqbdKey = next((key for key in cgmClasses if 'EQBD' in key), None)
    for selectedProfile in (profile for profile in cgmClasses if 'EQ_' in profile):
        print('Creating CO profile for:', selectedProfile)
        fullModeldict = cgmClasses[selectedProfile]['FullModel']
        contingencyEquipment = buildcontingencyEquipmentList(inputArgs, cgmClasses[selectedProfile], cgmClasses.get(eqbdKey, {'BaseVoltage': {}}))
        createContingencyProfile(fullModeldict, contingencies, contingencyEquipment, existingContingencies, pathToNewContingencies, selectedProfile)

    # Load newly created profiles into database for future comparison
    coProfiles = getCgmProfilesFromFolder(pathToNewContingencies)
    database = getJson(pathToDatabase)
    if database is None:
        database = {'OrdinaryContingency': {}, 'ContingencyEquipment': {}}
    # Append dictionaries horisontaly'
    for file in coProfiles.keys():
        for category in coProfiles[file].keys():
            if category == 'OrdinaryContingency':
                database[category].update(coProfiles[file][category])
            elif category == 'ContingencyEquipment':
                database[category].update(coProfiles[file][category])

    convertDictToJasonFile(database, pathToDatabase)


# Define input arguments as a dictionary
inputArgs = {
    # Boundary values for equipment
    'lineBoundaryKv': 100,
    'transformerBoundaryKv': 100,
    'synchronousMachineBoundaryMva': 50,
    'loadBoundaryKv': 100,

    # Directory path to get the CGMES profiles from
    'directoryPath': os.path.abspath(os.path.join('cgmProfiles'))
}
# Paths
pathToCgmClasses = os.path.abspath(os.path.join('scriptObjectsAsFiles', 'cgmClasses.json'))
pathToCgmHeader = os.path.abspath(os.path.join('scriptObjectsAsFiles', 'cgmClasses.txt'))
pathToContingencies = os.path.abspath(os.path.join('Database', 'storedContingencies.json'))
pathToNewContingencies = os.path.abspath(os.path.join('createdContingencies'))
pathToDatabase = os.path.abspath(os.path.join('database', 'storedContingencies.json'))
# Call main and start application
main(inputArgs)
