import sys
import os
from contingencyMethods import buildcontingencyEquipmentList, createContingencyProfile
from fileHandlingMethods import getCgmProfilesFromFolder, convertDictToJasonFile, createHeaderFileFromDict, getJson


def main(inputArgs):
    # Get all Equipment from the Equipment Profile
    #cgmClasses = getCgmProfilesFromFolder(inputArgs['directoryPath'])
    #convertDictToJasonFile(cgmClasses, pathToCgmClasses)
    #createHeaderFileFromDict(cgmClasses, pathToCgmHeader)

    # Get profiles
    cgmClasses = getJson(os.path.abspath(os.path.join('scriptObjectsAsFiles', 'cgmClasses.json')))

    # Get JSON database for currently defined ordinary contingencies
    contingenciesDatabase = getJson(pathToContingencies)

    # Create reverse dictionary(sort of) for quick lookup and comparison with potential new contingencies. key is equipmentMrid and value is contingencyEquipmentMrid
    existingContingencies = {}
    for key in contingenciesDatabase['ContingencyEquipment'].keys():
        equipmentMrid = contingenciesDatabase['ContingencyEquipment'][key]['ContingencyEquipment.Equipment']
        existingContingencies[equipmentMrid] = key

    # Create dictionary of equipment to create contingencies on
    eqbdKey = next((key for key in cgmClasses if 'EQBD' in key), None)
    for selectedProfile in (profile for profile in cgmClasses if 'EQ_' in profile):
        print('Creating CO profile for:', selectedProfile)
        fullModeldict = cgmClasses[selectedProfile]['FullModel']
        contingencyEquipment = buildcontingencyEquipmentList(inputArgs, cgmClasses[selectedProfile], cgmClasses.get(eqbdKey, {'BaseVoltage': {}}))
        createContingencyProfile(fullModeldict, contingenciesDatabase, contingencyEquipment, existingContingencies, pathToNewContingencies, selectedProfile)

    #  Loop Through newly created contingencies and contingencyEquipment and save new 
    newContingencies = getCgmProfilesFromFolder(os.path.abspath(os.path.join('createdContingencies')))
    for profile in newContingencies:
        for key, value in newContingencies[profile]['OrdinaryContingency'].items():
            if key not in contingenciesDatabase['OrdinaryContingency']:
                contingenciesDatabase['OrdinaryContingency'][key] = value

        for key, value in newContingencies[profile]['ContingencyEquipment'].items():
            if key not in contingenciesDatabase['ContingencyEquipment']:
                contingenciesDatabase['ContingencyEquipment'][key] = value
        
    # save Database
    convertDictToJasonFile(contingenciesDatabase, pathToDatabase)


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
pathToContingencies = os.path.abspath(os.path.join('database', 'storedContingencies.json'))
pathToNewContingencies = os.path.abspath(os.path.join('createdContingencies'))
pathToDatabase = os.path.abspath(os.path.join('database', 'storedContingencies.json'))
# Call main and start application
main(inputArgs)
