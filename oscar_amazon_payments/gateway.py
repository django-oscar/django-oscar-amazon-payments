import logging
import time
import datetime
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

        self.payload_template = {
            'AWSAccessKeyId': settings.AMAZON_PAYMENTS_ACCESS_KEY,
            'AmazonOrderReferenceId': self.amazon_order_reference_id,
            'SellerId': settings.AMAZON_PAYMENTS_SELLER_ID,
            'SignatureMethod': 'HmacSHA256',
            'SignatureVersion': '2',
            'Version': '2013-01-01',
        }

    def _do_request(self, payload):
        payload['Signature'] = self._calculate_signature(payload)
        return requests.post(AMAZON_PAYMENTS_URI, data=payload)

    def _canonicalize_payload(self, payload):
        canonical_form = (
            'POST\n' +
            settings.AMAZON_PAYMENTS_URL +
            '\n' +
            '/' +
            settings.AMAZON_PAYMENTS_URL_PATH +
            '/' +
            settings.AMAZON_PAYMENTS_URL_VERSION +
            '\n'
        )
        key_list = payload.keys()
        key_list.sort()
        values = map(payload.get, key_list)
        # Amazon encode spaces as %20 so replace an '+'
        url_string = urllib.urlencode(zip(key_list, values)).replace('+', '%20')
        canonical_form += url_string
        return canonical_form

    def _calculate_signature(self, payload):
        msg = self._canonicalize_payload(payload)
        sig = hmac.new(settings.AMAZON_PAYMENTS_SECRET_KEY, msg, hashlib.sha256).digest()
        return base64.encodestring(sig).strip()

    def _get_date(self):
        return time.strftime('%Y-%m-%d')

    def _get_urlencoded_timestamp(self):
        return datetime.datetime.now().isoformat()

    # ===
    # API
    # ===

    def get_order_reference_details(self):
        """
        GetOrderReferenceDetails

        self.amazon_order_reference_id is retrieved from the authenticate with amazon widget once the
        customer has authenticated
        """
        payload = self.payload_template.copy()

        payload['Action'] = GET_ORDER_REFERENCE
        payload['Timestamp'] = self._get_urlencoded_timestamp()

        return self._do_request(payload)

    def set_order_reference_details(self, amount, currency, order_id, note=None):
        """
        SetOrderReferenceDetails

        This must be called before displaying the wallet widget as the amount dictates which payment methods are
        available.
        """

        payload = self.payload_template.copy()

        payload['Action'] = SET_ORDER_REFERENCE
        payload['OrderReferenceAttributes.OrderTotal.Amount'] = amount
        payload['OrderReferenceAttributes.OrderTotal.CurrencyCode'] = currency
        if note:
            payload['OrderReferenceAttributes.SellerNote'] = note
        payload['OrderReferenceAttributes.SellerOrderAttributes.SellerOrderId'] = order_id
        payload['OrderReferenceAttributes.SellerOrderAttributes.StoreName'] = settings.AMAZON_PAYMENTS_STORE_NAME
        payload['Timestamp'] = self._get_urlencoded_timestamp()

        return self._do_request(payload)

    def confirm_order_reference(self):
        """
        ConfirmOrderReference
        """

        payload = self.payload_template.copy()

        payload['Action'] = CONFIRM_ORDER_REFERENCE
        payload['Timestamp'] = self._get_urlencoded_timestamp()

        return self._do_request(payload)

    def cancel_order_reference(self):
        """
        CancelOrderReference
        """

        payload = self.payload_template.copy()

        payload['Action'] = CANCEL_ORDER_REFERENCE
        payload['Timestamp'] = self._get_urlencoded_timestamp()

        return self._do_request(payload)

    def close_order_reference(self, closure_reason=''):
        """
        CloseOrderReference
        """

        payload = self.payload_template.copy()

        payload['Action'] = CLOSE_ORDER_REFERENCE
        payload['ClosureReason'] = closure_reason
        payload['Timestamp'] = self._get_urlencoded_timestamp()

        return self._do_request(payload)

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

        payload = self.payload_template.copy()

        payload['Action'] = AUTHORIZE,
        payload['AuthorizationAmount.Amount'] = amount
        payload['AuthorizationAmount.Currency'] = currency
        payload['AuthorizationReferenceId'] = authorization_reference_id
        payload['SellerAuthorizationNote'] = note
        payload['Timestamp'] = self._get_urlencoded_timestamp()
        payload['TransactionTimeout'] = transaction_timeout
        payload['CaptureNow'] = capture_now
        payload['SoftDescriptor'] = soft_descriptor

        return self._do_request(payload)

    def get_authorization_details(self):
        """
        GetAuthorizationDetails
        """

        payload = self.payload_template.copy()

        payload['Action'] = GET_AUTHORIZATION_DETAILS

        return self._do_request(payload)

    def close_authorization(self, closure_reason=''):
        """
        CloseAuthorization
        """

        payload = self.payload_template.copy()

        payload['Action'] = CLOSE_AUTHORIZATION
        payload['ClosureReason'] = closure_reason

        return self._do_request(payload)

    def capture(self, amount, currency, capture_reference_id, note='', soft_descriptor=''):
        """
        Capture the payment
        """

        payload = self.payload_template.copy()

        payload['Action'] = CAPTURE
        payload['CaptureReferenceId'] = capture_reference_id
        payload['CaptureAmount.Amount'] = amount
        payload['CaptureAmount.Currency'] = currency
        payload['SellerCaptureNote'] = note
        payload['SoftDescriptor'] = soft_descriptor
        payload['Timestamp'] = self._get_urlencoded_timestamp()

        return self._do_request(payload)

    def refund(self, capture_id, refund_amount, currency, refund_reference_id, note='', soft_descriptor=''):
        """
        Refund the payment
        """

        payload = self.payload_template.copy()

        payload['Action'] = REFUND
        payload['AmazonCaptureId'] = capture_id
        payload['RefundAmount.Amount'] = refund_amount
        payload['RefundAmount.Currency'] = currency
        payload['RefundReferenceId'] = refund_reference_id
        payload['SellerRefundNote'] = note
        payload['SoftDescriptor'] = soft_descriptor
        payload['Timestamp'] = self._get_urlencoded_timestamp()

        return self._do_request(payload)

    def get_refund_details(self, refund_reference_id):
        """
        GetRefundDetails
        """

        payload = self.payload_template.copy()

        payload['Action'] = GET_REFUND_DETAILS
        payload['RefundReferenceId'] = refund_reference_id
        payload['Timestamp'] = self._get_urlencoded_timestamp()

        return self._do_request(payload)

    def get_service_status(self):
        """
        GetServiceStatus
        """

        payload = self.payload_template.copy()

        payload['Action'] = GET_SERVICE_STATUS
        payload['Timestamp'] = self._get_urlencoded_timestamp()

        return self._do_request(payload)
