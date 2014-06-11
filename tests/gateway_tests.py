from mock import Mock

from django.test import TestCase

from oscar_amazon_payments.gateway import Gateway

STATUS_RESPONSE_XML = (
    '<?xml version="1.0"?>' +
    '<GetServiceStatusResponse xmlns="http://mws.amazonservices.com/schema/OffAmazonPayments/2013-01-01">' +
    '<GetServiceStatusResult>' +
    '<Status>GREEN</Status>' +
    '<Timestamp>2014-06-11T13:40:53.969Z</Timestamp>' +
    '</GetServiceStatusResult>' +
    '<ResponseMetadata>' +
    '<RequestId>bf4c5241-fdce-4f56-92b1-b2680c3068ae</RequestId>' +
    '</ResponseMetadata>' +
    '</GetServiceStatusResponse>'
)


class TestGateway(TestCase):

    def setUp(self):
        self.gateway = Gateway('1234567890')

    def test_current_status(self):
        self.gateway._do_request = Mock(return_value=STATUS_RESPONSE_XML)
        status = self.gateway.get_service_status()
        self.assertEqual(status, STATUS_RESPONSE_XML)
