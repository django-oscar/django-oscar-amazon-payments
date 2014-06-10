import logging
import datetime
import time
import requests
import hmac
import hashlib
import base64
import urllib

from django.conf import settings

logger = logging.getLogger('amazon-payments')

# Actions
AUTHORIZE = 'Authorize'
GET_AUTHORIZATION_DETAILS = 'GetAuthorizationDetails'
CLOSE_AUTHORIZATION = 'CloseAuthorization'
GET_ORDER_REFERENCE = 'GetOrderReferenceDetails'
SET_ORDER_REFERENCE = 'SetOrderReferenceDetails'
CONFIRM_ORDER_REFERENCE = 'ConfirmOrderReferenceDetails'
CANCEL_ORDER_REFERENCE = 'CancelOrderReferenceDetails'
CLOSE_ORDER_REFERENCE = 'CloseOrderReferenceDetails'
CAPTURE = 'Capture'
REFUND = 'Refund'
GET_REFUND_DETAILS = 'GetRefundDetails'
GET_SERVICE_STATUS = 'GetServiceStatus'

AMAZON_PAYMENTS_URI = 'https://{}/{}/{}'.format(
    settings.AMAZON_PAYMENTS_URL,
    settings.AMAZON_PAYMENTS_URL_PATH,
    settings.AMAZON_PAYMENTS_URL_VERSION
)


class Request(object):

    """
    Encapsulate Amazon Payments Request
    """


class Response(object):

    """
    Encapsulate Amazon Payments Response
    """


class Gateway(object):

    """
    Gateway to amazon payments
    """

    def __init__(self, amazon_order_reference_id):
        self.amazon_order_reference_id = amazon_order_reference_id

        self.payload = {
            'AWSAccessKeyId': settings.AMAZON_ACCESS_KEY,
            'AmazonOrderReferenceId': self.amazon_order_reference_id,
            'SellerId': settings.AMAZON_SELLER_ID,
            'SignatureMethod': 'HmacSHA256',
            'SignatureVersion': '2',
            'Version': '2013-01-01',
        }

    def _canonicalize_payload(self):
        canonical_form = (
            'POST\n' +
            settings.AMAZON_PAYMENTS_URL +
            '\n' +
            settings.AMAZON_PAYMENTS_URL_PATH.lower() +
            '\n' +
            settings.AMAZON_PAYMENTS_URL_VERSION +
            '\n'
        )
        key_list = []
        for key, value in self.payload.items():
            key_list.append(key)
        key_list = sorted(key_list)
        for key in key_list:
            canonical_form += urllib.quote_plus(key) + urllib.quote_plus(self.payload[key]) + '&'
        return canonical_form[:-1]

    def _calculate_signature(self):
        msg = self._canonicalize_payload()
        sig = hmac.new(settings.AMAZON_SECRET_KEY, msg.encode('utf-8'), hashlib.sha256).digest()
        return base64.b64encode(sig).decode()

    def _get_date(self):
        return time.strftime('%Y-%m-%d')

    def _get_urlencoded_timestamp(self):
        return urllib.quote_plus(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))

    # ===
    # API
    # ===

    def get_order_reference_details(self):
        """
        GetOrderReferenceDetails

        self.amazon_order_reference_id is retrieved from the authenticate with amazon widget once the
        customer has authenticated
        """
        self.payload['Action'] = GET_ORDER_REFERENCE
        self.payload['Timestamp'] = self._get_urlencoded_timestamp()
        self.payload['Signature'] = self._calculate_signature()

        return requests.post(AMAZON_PAYMENTS_URI, data=self.payload)

    def set_order_reference_details(self, amount, currency, order_id, note=None):
        """
        SetOrderReferenceDetails

        This must be called before displaying the wallet widget as the amount dictates which payment methods are
        available.
        """

        self.payload['Action'] = SET_ORDER_REFERENCE
        self.payload['AmazonOrderReferenceAttributes.OrderTotal.Amount'] = amount
        self.payload['OrderReferenceAttributes.OrderTotal.CurrencyCode'] = currency
        self.payload['OrderReferenceAttributes.SellerNote'] = note
        self.payload['OrderReferenceAttributes.SellerOrderAttributes.SellerOrderId'] = order_id
        self.payload['OrderReferenceAttributes.SellerOrderAttributes.StoreName'] = settings.AMAZON_STORE_NAME
        self.payload['Timestamp'] = self._get_urlencoded_timestamp()
        self.payload['Signature'] = self._calculate_signature()

        return requests.post(AMAZON_PAYMENTS_URI, data=self.payload)

    def confirm_order_reference(self):
        """
        ConfirmOrderReference
        """

        self.payload['Action'] = CONFIRM_ORDER_REFERENCE
        self.payload['Timestamp'] = self._get_urlencoded_timestamp()
        self.payload['Signature'] = self._calculate_signature()

        return requests.post(AMAZON_PAYMENTS_URI, data=self.payload)

    def cancel_order_reference(self):
        """
        CancelOrderReference
        """

        self.payload['Action'] = CANCEL_ORDER_REFERENCE
        self.payload['Timestamp'] = self._get_urlencoded_timestamp()
        self.payload['Signature'] = self._calculate_signature()

        return requests.post(AMAZON_PAYMENTS_URI, data=self.payload)

    def close_order_reference(self, closure_reason=''):
        """
        CloseOrderReference
        """

        self.payload['Action'] = CLOSE_ORDER_REFERENCE
        self.payload['ClosureReason'] = closure_reason
        self.payload['Timestamp'] = self._get_urlencoded_timestamp()
        self.payload['Signature'] = self._calculate_signature()

        return requests.post(AMAZON_PAYMENTS_URI, data=self.payload)

    def async_auth(self, amount, currency, note='', capture_now='false', soft_descriptor=''):
        """
        Asynchronous authorization
        """
        # Get the amazon async timeout value, defaults to sizty minutes
        transaction_timeout = getattr(settings, 'AMAZON_ASYNCHRONOUS_TIMEOUT', 60)
        return self._auth(
            amount,
            currency,
            self.amazon_order_reference_id,
            note,
            transaction_timeout,
            capture_now,
            soft_descriptor
        )

    def sync_auth(self, amount, currency, note='', capture_now='false', soft_descriptor=''):
        """
        Synchronous authorization
        """
        transaction_timeout = 0
        return self._auth(
            amount,
            currency,
            self.amazon_order_reference_id,
            note,
            transaction_timeout,
            capture_now,
            soft_descriptor
        )

    def _auth(self, amount, currency, authorization_reference_id, note, transaction_timeout, capture_now, soft_descriptor):
        """
        Completes the authorization request
        """

        self.payload['Action'] = AUTHORIZE,
        self.payload['AuthorizationAmount.Amount'] = amount
        self.payload['AuthorizationAmount.Currency'] = currency
        self.payload['AuthorizationReferenceId'] = authorization_reference_id
        self.payload['SellerAuthorizationNote'] = note
        self.payload['Timestamp'] = self._get_urlencoded_timestamp()
        self.payload['TransactionTimeout'] = transaction_timeout
        self.payload['CaptureNow'] = capture_now
        self.payload['SoftDescriptor'] = soft_descriptor
        self.payload['Signature'] = self._calculate_signature()

        return requests.post(AMAZON_PAYMENTS_URI, data=self.payload)

    def get_authorization_details(self):
        """
        GetAuthorizationDetails
        """

        self.payload['Action'] = GET_AUTHORIZATION_DETAILS
        self.payload['Signature'] = self._calculate_signature()

        return requests.post(AMAZON_PAYMENTS_URI, data=self.payload)

    def close_authorization(self, closure_reason=''):
        """
        CloseAuthorization
        """

        self.payload['Action'] = CLOSE_AUTHORIZATION
        self.payload['ClosureReason'] = closure_reason
        self.payload['Signature'] = self._calculate_signature()

        return requests.post(AMAZON_PAYMENTS_URI, data=self.payload)

    def capture(self, amount, currency, capture_reference_id, note='', soft_descriptor=''):
        """
        Capture the payment
        """

        self.payload['Action'] = CAPTURE
        self.payload['CaptureReferenceId'] = capture_reference_id
        self.payload['CaptureAmount.Amount'] = amount
        self.payload['CaptureAmount.Currency'] = currency
        self.payload['SellerCaptureNote'] = note
        self.payload['SoftDescriptor'] = soft_descriptor
        self.payload['Timestamp'] = self._get_urlencoded_timestamp()
        self.payload['Signature'] = self._calculate_signature()

        return requests.post(AMAZON_PAYMENTS_URI, data=self.payload)

    def refund(self, capture_id, refund_amount, currency, refund_reference_id, note='', soft_descriptor=''):
        """
        Refund the payment
        """

        self.payload['Action'] = REFUND
        self.payload['AmazonCaptureId'] = capture_id
        self.payload['RefundAmount.Amount'] = refund_amount
        self.payload['RefundAmount.Currency'] = currency
        self.payload['RefundReferenceId'] = refund_reference_id
        self.payload['SellerRefundNote'] = note
        self.payload['SoftDescriptor'] = soft_descriptor
        self.payload['Timestamp'] = self._get_urlencoded_timestamp()
        self.payload['Signature'] = self._calculate_signature()

        return requests.post(AMAZON_PAYMENTS_URI, data=self.payload)

    def get_refund_details(self, refund_reference_id):
        """
        GetRefundDetails
        """

        self.payload['Action'] = GET_REFUND_DETAILS
        self.payload['RefundReferenceId'] = refund_reference_id
        self.payload['Timestamp'] = self._get_urlencoded_timestamp()
        self.payload['Signature'] = self._calculate_signature()

        return requests.post(AMAZON_PAYMENTS_URI, data=self.payload)

    def get_service_status(self):
        """
        GetServiceStatus
        """

        self.payload['Action'] = GET_SERVICE_STATUS
        self.payload['Timestamp'] = self._get_urlencoded_timestamp()
        self.payload['Signature'] = self._calculate_signature()

        return requests.post(AMAZON_PAYMENTS_URI, data=self.payload)

if __name__ == "__main__":
    gateway = Gateway('123')
    print gateway._get_urlencoded_timestamp()
