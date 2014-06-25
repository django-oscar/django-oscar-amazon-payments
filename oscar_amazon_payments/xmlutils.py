from BeautifulSoup import BeautifulSoup as BS


def get_partial_address(xml):
    """
    Gets the partial address from the response xml
    """
    address = {}
    response_xml = BS(xml)
    address_xml = response_xml.find('physicaldestination')
    address['post_code'] = address_xml.find('postalcode').string
    address['city'] = address_xml.find('city').string
    address['country_code'] = address_xml.find('countrycode').string
    return address


def get_status(xml):
    """
    Get the amazon service status in a usable form
    """
    response_xml = BS(xml)
    return response_xml.find('status').string


def process_order_details(xml):
    # TODO flush out stub
    return xml
