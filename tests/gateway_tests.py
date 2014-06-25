from mock import Mock

from django.test import TestCase

from oscar_amazon_payments.gateway import Gateway
import mock_responses


class TestGateway(TestCase):

    def setUp(self):
        self.gateway = Gateway('1234567890')

    def test_current_status(self):
        self.gateway._do_request = Mock(return_value=mock_responses.STATUS_RESPONSE_XML)
        status = self.gateway.get_service_status()
        self.assertEqual(status, mock_responses.STATUS_RESPONSE_XML)

    def test_get_order_reference_details(self):
        self.gateway._do_request = Mock(return_value=mock_responses.ORDER_REFERENCE_DETAILS_XML)
        ref_details = self.gateway.get_order_reference_details()
        self.assertEqual(ref_details, mock_responses.ORDER_REFERENCE_DETAILS_XML)

    def test_set_order_reference_details(self):
        pass

    def test_confirm_order_reference(self):
        pass

    def test_cancel_order_reference(self):
        pass

    def test_close_order_reference(self):
        pass

    def test_async_auth(self):
        pass

    def test_sync_auth(self):
        pass

    def test_authorization_details(self):
        pass

    def test_close_authorization(self):
        pass

    def test_capture(self):
        pass

    def test_refund(self):
        pass

    def test_get_refund_details(self):
        pass

    def test_invalid_signature(self):
        pass
