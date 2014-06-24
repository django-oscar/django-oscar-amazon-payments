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

ORDER_REFERENCE_DETAILS_XML = (
    '<GetOrderReferenceDetailsResponse xmlns="http://mws.amazonservices.com/schema/OffAmazonPayments/2013-01-01">' +
    '<GetOrderReferenceDetailsResult>' +
    '<OrderReferenceDetails>' +
    '<AmazonOrderReferenceId>S02-4932843-1071433</AmazonOrderReferenceId>' +
    '<ExpirationTimestamp>2014-12-21T08:52:38.770Z</ExpirationTimestamp>' +
    '<Constraints>' +
    '<Constraint>' +
    '<ConstraintID>AmountNotSet</ConstraintID>' +
    '<Description>The seller has not set the amount for the Order Reference.</Description>' +
    '</Constraint>' +
    '</Constraints>' +
    '<IdList/>' +
    '<Destination>' +
    '<DestinationType>Physical</DestinationType>' +
    '<PhysicalDestination>' +
    '<PostalCode>SE1 5RB</PostalCode>' +
    '<CountryCode>GB</CountryCode>' +
    '<City>LONDON</City>' +
    '</PhysicalDestination>' +
    '</Destination>' +
    '<OrderReferenceStatus>' +
    '<State>Draft</State>' +
    '</OrderReferenceStatus>' +
    '<ReleaseEnvironment>Sandbox</ReleaseEnvironment>' +
    '<SellerOrderAttributes/>' +
    '<CreationTimestamp>2014-06-24T08:52:38.770Z</CreationTimestamp>' +
    '</OrderReferenceDetails>' +
    '</GetOrderReferenceDetailsResult>' +
    '<ResponseMetadata>' +
    '<RequestId>e13beadb-c4b1-4c0e-a5b8-b5f8dc2f33ac</RequestId>' +
    '</ResponseMetadata>' +
    '</GetOrderReferenceDetailsResponse>'
)
