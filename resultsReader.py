import xml.etree.ElementTree as ET

def read_xml(file_path):
    """Parse and return the root element of an XML file"""
    tree = ET.parse(file_path)
    return tree.getroot()

def print_xml_tree(element, level=0):
    """Print the XML tree structure"""
    if element.tag in ["deviceID", "nameVendor", "nameProduct", "nameModel", "versionHW", "versionSW", "versionFW", "serialNumber"]:
        print("  " * level + f"{element.tag}: {element.text.strip() if element.text else ''}")
    for child in element:
        print_xml_tree(child, level + 1)

# def find_elements(root, tag):
#     """Find all elements with a specific tag"""
#     return root.findall(tag)

# def get_element_text(element, tag):
#     """Get text content of a specific child element"""
#     child = element.find(tag)
#     return child.text if child is not None else None

# Example usage
if __name__ == "__main__":
    root = read_xml("your_file.xml")
    print_xml_tree(root)
    pass