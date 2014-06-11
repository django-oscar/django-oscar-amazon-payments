import random
import string

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from oscar.apps.payment.exceptions import UnableToTakePayment, InvalidGatewayRequestError

from oscar_amazon_payments import gateway
from oscar_amazon_payments.models import OrderTransaction

from oscar.core.loading import get_model

from BeautifulSoup import BeautifulSoup as BS

ShippingAddress = get_model('order', 'ShippingAddress')
Order = get_model('order', 'Order')
Country = get_model('address', 'Country')


class Facade(object):

    """
    A bridge between oscar's objects and the amazon payment interface
    """

    def __init__(self, amazon_order_reference_id):
        self.gateway = gateway.Gateway(amazon_order_reference_id)

    def handle_response(self, response):
        """
        Raises an exception if the response indicates an error has ocurred,
        if this method returns, we can assume that the response data is stored
        """
        pass

    def record_txn(self, order_number):
        OrderTransaction.objects.create(
            order_number=order_number
        )

    def fulfill_transaction(self):
        pass

    def refund_transaction(self):
        pass

    def cancel_transaction(self):
        pass

    def get_status(self):
        response = self.gateway.get_service_status()
        return response

    def _generate_authorization_reference_id(self):
        return ''.join([random.choice(string.ascii_letters) for n in xrange(30)])

    def get_shipping_address(self):
        response = self.gateway.get_order_reference_details()
        self.handle_response(response)
        response_xml = BS(response.content)
        address_xml = response_xml.find('physicaldestination')
        post_code = address_xml.find('postalcode').string
        city = address_xml.find('city').string
        country = Country.objects.get(iso_3166_1_a3=address_xml.find('countrycode').string)
        shipping_address = ShippingAddress(line1='', state=city, postcode=post_code, country=country)
        shipping_address.save()
        return shipping_address
