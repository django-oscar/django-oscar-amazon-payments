from mock import Mock

from django.test import TestCase

from oscar_amazon_payments.facade import Facade
import mock_responses


class MockResponse(object):
    content = ""


class TestFacade(TestCase):
    mock_response = MockResponse()

    def setUp(self):
        self.facade = Facade('1234567890')
        self.facade.gateway.get_service_status = Mock(return_value=self.mock_response)

    def test_current_status(self):
        self.mock_response.content = mock_responses.STATUS_RESPONSE_XML
        status = self.facade.get_status()
        self.assertEqual(status, "GREEN")
