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
    lineOverview = {}
    for acLineSegmentMrid in eqProfile['ACLineSegment']:
        lineMrid = eqProfile['ACLineSegment'][acLineSegmentMrid]['Equipment.EquipmentContainer']
        lineName = eqProfile['Line'][lineMrid]['IdentifiedObject.name']
        acLineName = eqProfile['ACLineSegment'][acLineSegmentMrid]['IdentifiedObject.name']
        acLineName = lineName + '.' + acLineName
        baseVoltageMrid = eqProfile['ACLineSegment'][acLineSegmentMrid]['ConductingEquipment.BaseVoltage']

        if lineMrid not in lineOverview:
            lineOverview[lineMrid] = {acLineSegmentMrid:{'acLineSegmentName':acLineName, 'BaseVoltageMrid':baseVoltageMrid}}
        else:
            lineOverview[lineMrid][acLineSegmentMrid] = {'acLineSegmentName':acLineName, 'BaseVoltageMrid':baseVoltageMrid}

    for mrid in eqProfile['ACLineSegment']:
        if eqProfile['ACLineSegment'][mrid].get('ConductingEquipment.BaseVoltage', '#N/A') in lineBaseVoltages:
            lineMrid = eqProfile['ACLineSegment'][mrid].get('Equipment.EquipmentContainer', '#N/A')
            lineName = eqProfile['Line'][lineMrid].get('IdentifiedObject.name', 'N/A')
            lineDescription = 'Line with ' + str(len(lineOverview[lineMrid])) + ' ACLineSegments'

            if lineMrid not in contingencyEquipment:
                contingencyEquipment[lineMrid] = ['Line', lineName, lineMrid, lineDescription,]
                

    # Append Transformers
    powerTransformerOverview = {}
    for powerTransformerEndMrid in eqProfile['PowerTransformerEnd']:
        powerTransformerMrid = eqProfile['PowerTransformerEnd'][powerTransformerEndMrid]['PowerTransformerEnd.PowerTransformer']
        powerTransformerName = eqProfile['PowerTransformer'][powerTransformerMrid]['IdentifiedObject.name']
        powerTransformerEndName = eqProfile['PowerTransformerEnd'][powerTransformerEndMrid]['IdentifiedObject.name']
        substationMrid = eqProfile['PowerTransformer'][powerTransformerMrid]['Equipment.EquipmentContainer']
        substationName = eqProfile['Substation'][substationMrid]['IdentifiedObject.name']
        powerTransformerEndFullName = substationName + '.' + powerTransformerName + '.' + powerTransformerEndName
        baseVoltageMrid =  eqProfile['PowerTransformerEnd'][powerTransformerEndMrid]['TransformerEnd.BaseVoltage']
        
        if powerTransformerMrid not in powerTransformerOverview:
            powerTransformerOverview[powerTransformerMrid] = {powerTransformerEndMrid:{'powerTransformerEndName':powerTransformerEndFullName,'BaseVoltageMrid':baseVoltageMrid}}
        else:
            powerTransformerOverview[powerTransformerMrid][powerTransformerEndMrid] = {'powerTransformerEndName':powerTransformerEndFullName,'BaseVoltageMrid':baseVoltageMrid}

    for mrid in eqProfile['PowerTransformerEnd']:
        if eqProfile['PowerTransformerEnd'][mrid].get('TransformerEnd.BaseVoltage', '#N/A') in transformerBaseVoltages:
            powerTransformerMrid = eqProfile['PowerTransformerEnd'][mrid].get('PowerTransformerEnd.PowerTransformer', '#N/A')
            powerTransformerName = _removeLastSegment(powerTransformerOverview[powerTransformerMrid][mrid]['powerTransformerEndName'])
            powerTransformerDescription = 'PowerTransformer with ' + str(len(powerTransformerOverview[powerTransformerMrid])) + ' windings'
            if powerTransformerMrid not in contingencyEquipment:
                contingencyEquipment[powerTransformerMrid] = ['PowerTransformer', powerTransformerName, powerTransformerMrid, powerTransformerDescription]

    # Append Loads
    # loadOverview = {}
    # for NonConformLoadMrid in eqProfile['NonConformLoad']:
    #     NonConformLoadName = eqProfile['NonConformLoad'][NonConformLoadMrid]['IdentifiedObject.name']
    #     substationMrid = eqProfile['NonConformLoad'][NonConformLoadMrid]['Equipment.EquipmentContainer']
        
    #     substationName = eqProfile['Substation'][substationMrid]['IdentifiedObject.name']
    #     NonConformLoadFullName = substationName + '.' + NonConformLoadName
        
    #     if NonConformLoadMrid not in loadOverview:
    #         loadOverview[NonConformLoadMrid] = {'NonConformLoadName':NonConformLoadFullName}

    for mrid in eqProfile['NonConformLoad']:
        voltageLevelMrid = eqProfile['NonConformLoad'][mrid].get('Equipment.EquipmentContainer', '#N/A')
        if eqProfile['VoltageLevel'][voltageLevelMrid].get('VoltageLevel.BaseVoltage', '#N/A') in loadBaseVoltages:
            loadMrid = mrid
            loadName = eqProfile['NonConformLoad'][mrid]['IdentifiedObject.name']
            loadDescription = eqProfile['NonConformLoad'][loadMrid].get('IdentifiedObject.description', 'This is for a NonConformLoad')
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

def _removeLastSegment(s):
    # Split the string by dots
    parts = s.rsplit('.', 1)
    # If there are at least two parts, return the first part
    if len(parts) > 1:
        return parts[0]
    # If there is no dot, return the original string
    return s
