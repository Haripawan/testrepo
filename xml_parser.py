import xmlschema

# Load the XSD file
schema = xmlschema.XMLSchema('path_to_your_xsd_file.xsd')

# Access and print the global elements
for elem in schema.elements.values():
    print(f'Element: {elem.name}, Type: {elem.type.name}')

# Access and print the global types
for type_ in schema.types.values():
    print(f'Type: {type_.name}')

# Validate an XML file against the schema
xml_file = 'path_to_your_xml_file.xml'
is_valid = schema.is_valid(xml_file)
print(f'Is the XML file valid? {is_valid}')

if not is_valid:
    # Get validation errors
    errors = schema.validate(xml_file)
    for error in errors:
        print(error)