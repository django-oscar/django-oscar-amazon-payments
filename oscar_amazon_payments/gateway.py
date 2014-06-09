import logging
import datetime
import time
import requests
import hmac
import hashlib
import base64

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
        self.self.amazon_order_reference_id = self.amazon_order_reference_id

    def _calculate_signature(self, msg):
        sig = hmac.new(settings.AMAZON_SECRET_KEY, msg.encode('utf-8'), hashlib.sha256).digest()
        return base64.b64encode(sig).decode()

    def _get_date(self):
        return time.strftime('%Y-%m-%d')

    def _get_urlencoded_timestamp(self):
        # TODO URL Encode before returning
        return datetime.datetime.now()

    # ===
    # API
    # ===

    def get_order_reference_details(self):
        """
        GetOrderReferenceDetails

        self.amazon_order_reference_id is retrieved from the authenticate with amazon widget once the
        customer has authenticated
        """

        payload = {
            'AWSAccessKeyId': settings.AMAZON_ACCESS_KEY,
            'Action': GET_ORDER_REFERENCE,
            'AmazonOrderReferenceId': self.amazon_order_reference_id,
            'SellerId': settings.AMAZON_SELLER_ID,
            'SignatureMethod': 'HmacSHA256',
            'SignatureVersion': 2,
            'Timestamp': self._get_urlencoded_timestamp,
            'Version': '2013-01-01',
            'Signature': self._calculate_signature(),
        }

        return requests.post(settings.AMAZON_PAYMENTS_URL, data=payload)

    def set_order_reference_details(self, amount, currency, order_id, note=None):
        """
        SetOrderReferenceDetails

        This must be called before displaying the wallet widget as the amount dictates which payment methods are
        available.
        """

        payload = {
            'AWSAccessKeyId': settings.AMAZON_ACCESS_KEY,
            'Action': SET_ORDER_REFERENCE,
            'AmazonOrderReferenceId': self.amazon_order_reference_id,
            'AmazonOrderReferenceAttributes.OrderTotal.Amount': amount,
            'OrderReferenceAttributes.OrderTotal.CurrencyCode': currency,
            'OrderReferenceAttributes.SellerNote': note,
            'OrderReferenceAttributes.SellerOrderAttributes.SellerOrderId': order_id,
            'OrderReferenceAttributes.SellerOrderAttributes.StoreName': settings.AMAZON_STORE_NAME,
            'SellerId': settings.AMAZON_SELLER_ID,
            'SignatureMethod': 'HmacSHA256',
            'SignatureVersion': 2,
            'Timestamp': self._get_urlencoded_timestamp,
            'Version': '2013-01-01',
            'Signature': self._calculate_signature(),
        }

        return requests.post(settings.AMAZON_PAYMENTS_URL, data=payload)

    def confirm_order_reference(self):
        """
        ConfirmOrderReference
        """

        payload = {
            'AWSAccessKeyId': settings.AMAZON_ACCESS_KEY,
            'Action': CONFIRM_ORDER_REFERENCE,
            'AmazonOrderReferenceId': self.amazon_order_reference_id,
            'SellerId': settings.AMAZON_SELLER_ID,
            'SignatureMethod': 'HmacSHA256',
            'SignatureVersion': 2,
            'Timestamp': self._get_urlencoded_timestamp,
            'Version': '2013-01-01',
            'Signature': self._calculate_signature(),
        }

        return requests.post(settings.AMAZON_PAYMENTS_URL, data=payload)

    def cancel_order_reference(self):
        """
        CancelOrderReference
        """

        payload = {
            'AWSAccessKeyId': settings.AMAZON_ACCESS_KEY,
            'Action': CANCEL_ORDER_REFERENCE,
            'AmazonOrderReferenceId': self.amazon_order_reference_id,
            'SellerId': settings.AMAZON_SELLER_ID,
            'SignatureMethod': 'HmacSHA256',
            'SignatureVersion': 2,
            'Timestamp': self._get_urlencoded_timestamp,
            'Version': '2013-01-01',
            'Signature': self._calculate_signature(),
        }

        return requests.post(settings.AMAZON_PAYMENTS_URL, data=payload)

    def close_order_reference(self, closure_reason=''):
        """
        CloseOrderReference
        """

        payload = {
            'AWSAccessKeyId': settings.AMAZON_ACCESS_KEY,
            'Action': CLOSE_ORDER_REFERENCE,
            'AmazonOrderReferenceId': self.amazon_order_reference_id,
            'ClosureReason': closure_reason,
            'SellerId': settings.AMAZON_SELLER_ID,
            'SignatureMethod': 'HmacSHA256',
            'SignatureVersion': 2,
            'Timestamp': self._get_urlencoded_timestamp,
            'Version': '2013-01-01',
            'Signature': self._calculate_signature(),
        }

        return requests.post(settings.AMAZON_PAYMENTS_URL, data=payload)

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

        payload = {
            'AWSAccessKeyId': settings.AMAZON_ACCESS_KEY,
            'Action': AUTHORIZE,
            'AmazonOrderReferenceId': self.amazon_order_reference_id,
            'AuthorizationAmount.Amount': amount,
            'AuthorizationAmount.Currency': currency,
            'AuthorizationReferenceId': authorization_reference_id,
            'SellerAuthorizationNote': note,
            'SellerId': settings.AMAZON_SELLER_ID,
            'SignatureMethod': 'HmacSHA256',
            'SignatureVersion': 2,
            'Timestamp': self._get_urlencoded_timestamp(),
            'TransactionTimeout': transaction_timeout,
            'CaptureNow': capture_now,
            'SoftDescriptor': soft_descriptor,
            'Version': '2013-01-01',
            'Signature': self._calculate_signature(),
        }

        return requests.post(settings.AMAZON_PAYMENTS_URL, data=payload)

    def get_authorization_details(self):
        """
        GetAuthorizationDetails
        """

        payload = {
            'AWSAccessKeyId': settings.AMAZON_ACCESS_KEY,
            'Action': GET_AUTHORIZATION_DETAILS,
            'AmazonOrderReferenceId': self.amazon_order_reference_id,
            'SellerId': settings.AMAZON_SELLER_ID,
            'SignatureMethod': 'HmacSHA256',
            'SignatureVersion': 2,
            'Timestamp': self._get_urlencoded_timestamp(),
            'Version': '2013-01-01',
            'Signature': self._calculate_signature(),
        }

        return requests.post(settings.AMAZON_PAYMENTS_URL, data=payload)

    def close_authorization(self, closure_reason=''):
        """
        CloseAuthorization
        """

        payload = {
            'AWSAccessKeyId': settings.AMAZON_ACCESS_KEY,
            'Action': CLOSE_AUTHORIZATION,
            'AmazonOrderReferenceId': self.amazon_order_reference_id,
            'SellerId': settings.AMAZON_SELLER_ID,
            'ClosureReason': closure_reason,
            'SignatureMethod': 'HmacSHA256',
            'SignatureVersion': 2,
            'Timestamp': self._get_urlencoded_timestamp(),
            'Version': '2013-01-01',
            'Signature': self._calculate_signature(),
        }

        return requests.post(settings.AMAZON_PAYMENTS_URL, data=payload)

    def capture(self, amount, currency, capture_reference_id, note='', soft_descriptor=''):
        """
        Capture the payment
        """

        payload = {
            'AWSAccessKeyId': settings.AMAZON_ACCESS_KEY,
            'Action': CAPTURE,
            'AmazonAuthorizationId': self.amazon_order_reference_id,
            'CaptureReferenceId': capture_reference_id,
            'CaptureAmount.Amount': amount,
            'CaptureAmount.Currency': currency,
            'SellerCaptureNote': note,
            'SoftDescriptor': soft_descriptor,
            'SellerId': settings.AMAZON_SELLER_ID,
            'SignatureMethod': 'HmacSHA256',
            'SignatureVersion': 2,
            'Timestamp': self._get_urlencoded_timestamp(),
            'Version': '2013-01-01',
            'Signature': self._calculate_signature(),
        }

        return requests.post(settings.AMAZON_PAYMENTS_URL, data=payload)

    def refund(self, capture_id, refund_amount, currency, refund_reference_id, note='', soft_descriptor=''):
        """
        Refund the payment
        """

        payload = {
            'AWSAccessKeyId': settings.AMAZON_ACCESS_KEY,
            'Action': REFUND,
            'AmazonCaptureId': capture_id,
            'RefundAmount.Amount': refund_amount,
            'RefundAmount.Currency': currency,
            'RefundReferenceId': refund_reference_id,
            'SellerRefundNote': note,
            'SoftDescriptor': soft_descriptor,
            'SellerId': settings.AMAZON_SELLER_ID,
            'SignatureMethod': 'HmacSHA256',
            'SignatureVersion': 2,
            'Timestamp': self._get_urlencoded_timestamp(),
            'Version': '2013-01-01',
            'Signature': self._calculate_signature(),
        }

        return requests.post(settings.AMAZON_PAYMENTS_URL, data=payload)

    def get_refund_details(self, refund_reference_id):
        """
        GetRefundDetails
        """

        payload = {
            'AWSAccessKeyId': settings.AMAZON_ACCESS_KEY,
            'Action': GET_REFUND_DETAILS,
            'RefundReferenceId': refund_reference_id,
            'SellerId': settings.AMAZON_SELLER_ID,
            'SignatureMethod': 'HmacSHA256',
            'SignatureVersion': 2,
            'Timestamp': self._get_urlencoded_timestamp(),
            'Version': '2013-01-01',
            'Signature': self._calculate_signature(),
        }

        return requests.post(settings.AMAZON_PAYMENTS_URL, data=payload)

    def get_service_status(self):
        """
        GetServiceStatus
        """

        payload = {
            'AWSAccessKeyId': settings.AMAZON_ACCESS_KEY,
            'Action': GET_SERVICE_STATUS,
            'SellerId': settings.AMAZON_SELLER_ID,
            'SignatureMethod': 'HmacSHA256',
            'SignatureVersion': 2,
            'Timestamp': self._get_urlencoded_timestamp(),
            'Version': '2013-01-01',
            'Signature': self._calculate_signature(),
        }

        return requests.post(settings.AMAZON_PAYMENTS_URL, data=payload)
