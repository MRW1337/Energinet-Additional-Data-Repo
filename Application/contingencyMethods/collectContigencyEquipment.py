def buildcontingencyEquipmentList(inputArgs, eqProfile, eqbdProfile):

    # Gather basevoltage from eq and boundary into 1 dictionary
    baseVoltage = {}
    baseVoltage.update(eqProfile)
    baseVoltage.update(eqbdProfile)

    # Create dictionaries for comparison with equipment based on requirement specifications
    lineBaseVoltages = _getBaseVoltageDictionary(baseVoltage['BaseVoltage'], inputArgs['lineBoundaryKv'])
    transformerBaseVoltages = _getBaseVoltageDictionary(baseVoltage['BaseVoltage'], inputArgs['transformerBoundaryKv'])
    loadBaseVoltages = _getBaseVoltageDictionary(baseVoltage['BaseVoltage'], inputArgs['loadBoundaryKv'])

    # Create dictionary of equipment to create contingencies on
    contingencyEquipment = {}

    # Append Lines
    for mrid in eqProfile['ACLineSegment']:
        if eqProfile['ACLineSegment'][mrid].get('ConductingEquipment.BaseVoltage', '#N/A') in lineBaseVoltages:
            lineMrid = eqProfile['ACLineSegment'][mrid].get('Equipment.EquipmentContainer', '#N/A')
            lineName = eqProfile['Line'][lineMrid].get('IdentifiedObject.name', 'N/A')
            lineDescription = eqProfile['Line'][lineMrid].get('IdentifiedObject.description', 'N/A')
            if lineMrid not in contingencyEquipment:
                contingencyEquipment[lineMrid] = ['Line', lineName, lineMrid, lineDescription,]

    # Append Transformers
    for mrid in eqProfile['PowerTransformerEnd']:
        if eqProfile['PowerTransformerEnd'][mrid].get('TransformerEnd.BaseVoltage', '#N/A') in transformerBaseVoltages:
            powerTransformerMrid = eqProfile['PowerTransformerEnd'][mrid].get('PowerTransformerEnd.PowerTransformer', '#N/A')
            powerTransformerName = eqProfile['PowerTransformer'][powerTransformerMrid].get('IdentifiedObject.name', 'N/A')
            powerTransformerDescription = eqProfile['PowerTransformer'][powerTransformerMrid].get('IdentifiedObject.description', 'N/A')
            if powerTransformerMrid not in contingencyEquipment:
                contingencyEquipment[powerTransformerMrid] = ['PowerTransformer', powerTransformerName, powerTransformerMrid, powerTransformerDescription]

    # Append Loads
    for mrid in eqProfile['NonConformLoad']:
        voltageLevelMrid = eqProfile['NonConformLoad'][mrid].get('Equipment.EquipmentContainer', '#N/A')
        if eqProfile['VoltageLevel'][voltageLevelMrid].get('VoltageLevel.BaseVoltage', '#N/A') in loadBaseVoltages:
            loadMrid = mrid
            loadName = eqProfile['NonConformLoad'][mrid].get('IdentifiedObject.name', 'N/A')
            loadDescription = eqProfile['NonConformLoad'][loadMrid].get('IdentifiedObject.description', 'N/A')
            if loadMrid not in contingencyEquipment:
                contingencyEquipment[loadMrid] = ['Load', loadName, loadMrid, loadDescription]

    # Append Synchronous Machines
    for mrid in eqProfile['SynchronousMachine']:
        generatingUnitMrid = eqProfile['SynchronousMachine'][mrid].get('RotatingMachine.GeneratingUnit', '#N/A')
        # generatingunitdict = eqProfile['GeneratingUnit'].get(generatingUnitMrid)
        maxOperatingPower = (eqProfile['GeneratingUnit'].get(generatingUnitMrid, {}).get('GeneratingUnit.maxOperatingP')
                             or eqProfile['ThermalGeneratingUnit'].get(generatingUnitMrid, {}).get('GeneratingUnit.maxOperatingP')
                             or eqProfile['WindGeneratingUnit'].get(generatingUnitMrid, {}).get('GeneratingUnit.maxOperatingP')
                             or '0')

        if float(maxOperatingPower) > inputArgs['synchronousMachineBoundaryMva']:
            synchronousMachineMrid = mrid
            synchronousMachineName = eqProfile['SynchronousMachine'].get('IdentifiedObject.name', 'N/A')
            synchronousMachineDescription = eqProfile['SynchronousMachine'][synchronousMachineMrid].get('IdentifiedObject.description', 'N/A')
            if synchronousMachineMrid not in contingencyEquipment:
                contingencyEquipment[synchronousMachineMrid] = ['SynchronousMachine', synchronousMachineName, synchronousMachineMrid, synchronousMachineDescription]

    return contingencyEquipment


def _getBaseVoltageDictionary(eqDictionary, voltageBoundary):
    baseVoltages = {}
    for key in eqDictionary:
        if float(eqDictionary[key]['BaseVoltage.nominalVoltage']) > voltageBoundary:
            baseVoltages[key] = eqDictionary[key]

    return baseVoltages
