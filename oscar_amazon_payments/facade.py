import random
import string

import xmlutils

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from oscar.apps.payment.exceptions import UnableToTakePayment, InvalidGatewayRequestError
from oscar_amazon_payments import gateway
from oscar_amazon_payments.models import OrderTransaction

from oscar.core.loading import get_model

ShippingAddress = get_model('order', 'ShippingAddress')
Order = get_model('order', 'Order')
Country = get_model('address', 'Country')


class Facade(object):

    """
    A bridge between oscar's objects and the amazon payment interface
    """

    def __init__(self, amazon_order_reference_id):
        self.gateway = gateway.Gateway(amazon_order_reference_id)
        #TODO - generate real order id
        self.order_id = '1234'

    def handle_response(self, response):
        """
        Raises an exception if the response indicates an error has ocurred,
        if this method returns, we can assume that the response data is stored
        """
        pass

    def record_txn(self, order_number):
        """
        This method records the transaction details in the database for auditing
        """
        OrderTransaction.objects.create(
            order_number=order_number
        )

    def set_order_details(self, amount, currency=settings.AMAZON_PAYMENTS_CURRENCY, note=None):
        """
        Set the amount and currency for the order
        """
        response = self.gateway.set_order_reference_details(amount, currency, self.order_id, note)
        self.handle_response(response)
        return xmlutils.process_order_details(response.content)

    def confirm_order_details(self):
        """
        Confirms the order details with amazon

        This method triggers the sending of the amazon confirmation email to the customer
        """
        response = self.gateway.confirm_order_reference()
        self.handle_response(response)
        return xmlutils.process_order_details_confirmation(response.content)

    def fulfill_transaction(self):
        pass

    def refund_transaction(self):
        pass

    def cancel_transaction(self):
        pass

    def get_status(self):
        """
        Get the current service status of the amazon payments API

        Returns:

        GREEN : Service is operating normally
        GREEN_I: Service is operating normally, more info provided
        YELLOW: The service is experience higher than normal error rates or degraded performance
        RED; Service is unavailable

        In any case other than GREEN, call get_status_with_info for more information about the service status
        """
        response = self.gateway.get_service_status()
        return xmlutils.get_status(response.content)

    def get_status_with_info(self):
        pass

    def get_partial_shipping_address(self):
        """
        Get the partial shipping address from amazon
        """
        response = self.gateway.get_order_reference_details()
        self.handle_response(response)
        address = xmlutils.get_partial_address(response.content)
        country = Country.objects.get(iso_3166_1_a3=address['country_code'])
        shipping_address = ShippingAddress(line1='', state=address['city'], postcode=address['post_code'], country=country)
        shipping_address.save()
        return shipping_address

    def get_full_shipping_address(self):
        """
        Get the full shipping address from amazon

        TODO - if we have already fetched the shipping address, get it from the database and not amazon

        but if we have only fetched a partial address, get the rest from amazon and update the database
        """
        response = self.gateway.get_order_reference_details()
        self.handle_response(response)
        address = xmlutils.get_full_address(response.content)
        country = Country.objects.get(iso_3166_1_a3=address['country_code'])
        shipping_address = ShippingAddress(line1=address['line_1'], state=address['city'], postcode=address['post_code'], country=country)
        shipping_address.save()
        return shipping_address

    def _generate_authorization_reference_id(self):
        """
        Generates an authorization reference id, this will be saved in the database transaction table
        """
        return ''.join([random.choice(string.ascii_letters) for n in xrange(30)])
