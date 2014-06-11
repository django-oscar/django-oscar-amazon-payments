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
