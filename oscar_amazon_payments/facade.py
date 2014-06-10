import random
import string

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

    def handle_response(self):
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
        import ipdb; ipdb.set_trace()
        return response.content
