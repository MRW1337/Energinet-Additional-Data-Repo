import uuid
import xml.etree.ElementTree as ET
import os
from xml.dom import minidom
from datetime import datetime


def createContingencyProfile(fullModeldict, contingency, contingencyEquipment, existingContingencies, pathToNewContingencies, selectedProfile):

    # Define namespaces
    namespaces = {
        'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
        'eumd': 'http://entsoe.eu/ns/Metadata-European#',
        'eu': 'http://iec.ch/TC57/CIM100-European#',
        'nc': 'http://entsoe.eu/ns/nc#',
        'prov': 'http://www.w3.org/ns/prov#',
        'md': 'http://iec.ch/TC57/61970-552/ModelDescription/1#',
        'skos': 'http://www.w3.org/2004/02/skos/core#',
        'dcat': 'http://www.w3.org/ns/dcat#',
        'cim': 'http://iec.ch/TC57/CIM100#',
        'dcterms': 'http://purl.org/dc/terms/#'
    }

    # Create the root element and set the namespaces
    rdf = ET.Element('rdf:RDF', {
        'xmlns:rdf': namespaces['rdf'],
        'xmlns:eumd': namespaces['eumd'],
        'xmlns:eu': namespaces['eu'],
        'xmlns:nc': namespaces['nc'],
        'xmlns:prov': namespaces['prov'],
        'xmlns:md': namespaces['md'],
        'xmlns:skos': namespaces['skos'],
        'xmlns:dcat': namespaces['dcat'],
        'xmlns:cim': namespaces['cim'],
        'xmlns:dcterms': namespaces['dcterms']
    })

    # Create the FullModel element
    coMrid = str(uuid.uuid4())
    full_model = ET.SubElement(rdf, 'md:FullModel', {'rdf:about': 'urn:uuid:' + '_' + coMrid})
    # Add child elements
    eqModelMrid = list(fullModeldict.keys())[0]
    ET.SubElement(full_model, 'dcterms:identifier').text = coMrid
    ET.SubElement(full_model, 'dcterms:conformsTo').text = 'https://ap.cim4.eu/Contingency-EU/2.3'
    ET.SubElement(full_model, 'eumd:Model.applicationSoftware').text = 'Pluto - Additional Data'
    ET.SubElement(full_model, 'dcterms:Model.description').text = 'Contingencies for:' + fullModeldict[eqModelMrid]['Model.description']
    ET.SubElement(full_model, 'prov:Model.generatedAtTime').text = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    ET.SubElement(full_model, 'dcterms:publisher', {'rdf:resource': "https://www.energinet.dk/Pluto/AdditionalData"})
    ET.SubElement(full_model, 'dcterms:Model.references', {'rdf:resource': '#_' + eqModelMrid})
    ET.SubElement(full_model, 'dcat:Model.keyword').text = 'CO'
    ET.SubElement(full_model, 'dcat:version').text = str(1)
    ET.SubElement(full_model, 'dcat:Model.startDate').text = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    ET.SubElement(full_model, 'dcat:Model.endDate').text = str(datetime.now().replace(year=datetime.now().year + 1).strftime("%Y-%m-%d %H:%M:%S"))

    # loop through list of contingencies to create
    for key, attributes in contingencyEquipment.items():
        key = key[1:]
        # check if equipmentmrid(key) is not an existing contingency
        if key not in existingContingencies:
            contingencyEquipmentMrid = str(uuid.uuid4())
            ordinaryContingencyMrid = str(uuid.uuid4())
            ocNameText = 'ordinaryContingency-' + attributes[1]
            ocDescriptionText = ''
            ocNormalMustStudyText = 'true'
            ceNameText = attributes[1]
            ceDescriptionText = attributes[3]
            ceContingentStatusText = 'http://iec.ch/TC57/CIM100#ContingencyEquipmentStatusKind.outOfService'
        else:
            contingencyEquipmentMrid = existingContingencies[key]
            ordinaryContingencyMrid = contingency['ContingencyEquipment'][contingencyEquipmentMrid]['ContingencyElement.Contingency']
            ocNameText = contingency['OrdinaryContingency'][ordinaryContingencyMrid]['IdentifiedObject.name']
            ocDescriptionText = contingency['OrdinaryContingency'][ordinaryContingencyMrid].get('IdentifiedObject.description', None)
            ocNormalMustStudyText = contingency['OrdinaryContingency'][ordinaryContingencyMrid]['Contingency.normalMustStudy']
            ceNameText = contingency['ContingencyEquipment'][contingencyEquipmentMrid]['IdentifiedObject.name']
            ceDescriptionText = contingency['ContingencyEquipment'][contingencyEquipmentMrid]['IdentifiedObject.description']
            ceContingentStatusText = contingency['ContingencyEquipment'][contingencyEquipmentMrid]['ContingencyEquipment.contingentStatus']

        # Create OrdinaryContingency element
        ordinaryContingency = ET.SubElement(rdf, 'nc:OrdinaryContingency')
        ordinaryContingency.set('rdf:ID', '_' + ordinaryContingencyMrid)
        ocName = ET.SubElement(ordinaryContingency, 'cim:IdentifiedObject.name')
        ocName.text = ocNameText
        ocDescription = ET.SubElement(ordinaryContingency, 'cim:IdentifiedObject.description')
        ocDescription.text = ocDescriptionText
        ocMrid = ET.SubElement(ordinaryContingency, 'cim:IdentifiedObject.mRID')
        ocMrid.text = ordinaryContingencyMrid
        ocNormalMustStudy = ET.SubElement(ordinaryContingency, 'nc:Contingency.normalMustStudy')
        ocNormalMustStudy.set('rdf:resource', ocNormalMustStudyText)

        # Create ContingencyEquipment element
        contingencyEquipment = ET.SubElement(rdf, 'cim:ContingencyEquipment')
        contingencyEquipment.set('rdf:ID', '_' + contingencyEquipmentMrid)
        ceName = ET.SubElement(contingencyEquipment, 'cim:IdentifiedObject.name')
        ceName.text = ceNameText
        ceDescription = ET.SubElement(contingencyEquipment, 'cim:IdentifiedObject.description')
        ceDescription.text = ceDescriptionText
        ceMrid = ET.SubElement(contingencyEquipment, 'cim:IdentifiedObject.mRID')
        ceMrid.text = contingencyEquipmentMrid
        ceContingency = ET.SubElement(contingencyEquipment, 'cim:ContingencyElement.Contingency')
        ceContingency.set('rdf:resource', '#_' + ordinaryContingencyMrid)
        ceContingent_status = ET.SubElement(contingencyEquipment, 'cim:ContingencyEquipment.contingentStatus')
        ceContingent_status.set('rdf:resource', ceContingentStatusText)
        ceEquipment = ET.SubElement(contingencyEquipment, 'cim:ContingencyEquipment.Equipment')
        ceEquipment.set('rdf:resource', f'#_{key}')

    pretty_xml = prettify_xml(rdf)

    # Write to a file
    path = os.path.abspath(os.path.join(pathToNewContingencies, selectedProfile.replace('_EQ', '_CO')))

    with open(path, 'w', encoding='utf-8') as f:
        f.write(pretty_xml)

    print('XML file created successfully.')


# Function to prettify the XML
def prettify_xml(elem):
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent='  ')
