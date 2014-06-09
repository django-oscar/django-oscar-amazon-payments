from django import http
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.conf import settings
from django.utils.translation import ugettext as _

from oscar.apps.checkout.views import PaymentDetailsView as OscarPaymentDetailsView
from oscar.apps.payment.forms import BankcardForm
from oscar.apps.payment.models import SourceType, Source
from oscar.apps.order.models import ShippingAddress
from oscar.apps.address.models import UserAddress

from oscar_amazon_payments.facade import Facade


class PaymentDetailsView(OscarPaymentDetailsView):

    def get_context_data(self, **kwargs):
        # Add bankcard form to the template context
        ctx = super(PaymentDetailsView, self).get_context_data(**kwargs)
        ctx['bankcard_form'] = kwargs.get('bankcard_form', BankcardForm())
        return ctx

    def handle_payment_details_submission(self, request):
        # Check bankcard form is valid
        bankcard_form = BankcardForm(request.POST)
        if bankcard_form.is_valid():
            return self.render_preview(
                request, bankcard_form=bankcard_form)

        # Form invalid - re-render
        return self.render_payment_details(
            request, bankcard_form=bankcard_form)

    def handle_place_order_submission(self, request):
        bankcard_form = BankcardForm(request.POST)
        if bankcard_form.is_valid():
            submission = self.build_submission(
                payment_kwargs={
                    'bankcard_form': bankcard_form
                })
            return self.submit(**submission)

        messages.error(request, _("Invalid submission"))
        return http.HttpResponseRedirect(
            reverse('checkout:payment-details'))

    def build_submission(self, **kwargs):
        # Ensure the shipping address is part of the payment keyword args
        submission = super(PaymentDetailsView, self).build_submission(**kwargs)
        submission['payment_kwargs']['shipping_address'] = submission[
            'shipping_address']
        return submission

    def handle_payment(self, order_number, total, **kwargs):
        # Make request to Amazon Payments - if there any problems (eg bankcard
        # not valid / request refused by bank) then an exception would be
        # raised and handled)
        facade = Facade()

        bankcard = kwargs['bankcard_form'].bankcard
        amazon_payments_ref = facade.pre_authorise(
            order_number, total.incl_tax, bankcard)

        # Request was successful - record the "payment source".  As this
        # request was a 'pre-auth', we set the 'amount_allocated' - if we had
        # performed an 'auth' request, then we would set 'amount_debited'.
        source_type, _ = SourceType.objects.get_or_create(name='AmazonPayments')
        source = Source(source_type=source_type,
                        currency=settings.AMAZON_PAYMENTS_CURRENCY,
                        amount_allocated=total.incl_tax,
                        reference=amazon_payments_ref)
        self.add_payment_source(source)

        # Also record payment event
        self.add_payment_event('pre-auth', total.incl_tax)
