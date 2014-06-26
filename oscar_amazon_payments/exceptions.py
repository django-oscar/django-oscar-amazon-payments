"""
Exceptions used to translate Amazon payments failures into python exceptions
that can be thrown by the gateway and handled by the facade/views

see the amazon documentation:

https://images-na.ssl-images-amazon.com/images/G/02/mwsportal/doc/en_US/offamazonpayments/AmazonPaymentsAdvancedIntegrationGuide.pdf

page 50 onwards on how to handle these errors
"""


class AuthorizeInvalidPaymentMethod(Exception):

    """
    Indicates that there was a problem with the payment method selected.  The
    order reference object will have been moved to the Suspended state
    """
    pass


class AuthorizeAmazonRejectedPayment(Exception):

    """
    Amazon declined this authorization.  You can retry the authorize operation
    if the order reference is still in the open state
    """
    pass


class AuthorizeProcessingFailure(Exception):

    """
    Amazon internal processing error, you can retry in 2 minutes
    """
    pass


class AuthorizeTransactionTimedOut(Exception):

    """
    In async mode, indicates that Authorize operation was not processed within
    the default timeouit period of 24 hours or within the time period specified
    in the original auth call
    """
    pass


class AuthorizeTransactionTimeoutReached(Exception):

    """
    In sync mode, indicates that Amazon could not process your request within
    6 - 8 seconds
    """
    pass


class CaptureAmazonRejected(Exception):

    """
    Indicates that Amazon declined the capture.  It is likely that the order
    reference and the auth object were closed, but if the order reference is
    still open, you can make another call to authorize and retry the capture
    """
    pass


class CaptureProcessingFailure(Exception):

    """
    Indicates an internal amazon processing error, you can retry in 2 minutes
    """
    pass


class RefundAmazonRejected(Exception):

    """
    Indicates that amazon declined the refund.  You need to get in touch with
    the customer to arrange a difference refund method
    """
    pass


class RefundProcessingFailure(Exception):

    """
    Indcates either:

    1. Amazon had an internal error
    2. The buyer has already received a refund from another method

    You need to check seller central on the amazon site and if there is no claim
    present, retry the refund in 2 minutes
    """
    pass
