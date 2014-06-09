import random
import string

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from oscar.apps.payment.exceptions import UnableToTakePayment, InvalidGatewayRequestError

from oscar_amazon_payments import gateway
from oscar_amazon_payments.models import OrderTransaction


class Facade(object):

    """
    A bridge between oscar's objects and the amazon payment interface
    """

    def __init__(self, *args, **kwargs):
        self.gateway = gateway.Gateway()

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

    def _generate_authorization_reference_id(self):
        return ''.join([random.choice(string.ascii_letters) for n in xrange(30)])
