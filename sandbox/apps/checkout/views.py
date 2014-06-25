from django import http
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.conf import settings
from django.utils.translation import ugettext as _
from django.views import generic
from django.forms.models import model_to_dict

from oscar.apps.checkout.views import ShippingAddressView as OscarShippingAddressView, PaymentDetailsView as OscarPaymentDetailsView
from oscar.apps.checkout.views import ShippingMethodView as OscarShippingMethodView
from oscar.apps.payment.forms import BankcardForm
from oscar.apps.payment.models import SourceType, Source

from oscar_amazon_payments.facade import Facade


class PaymentDetailsView(OscarPaymentDetailsView):

    def get(self, *args, **kwargs):
        self.reference_id = self.request.GET.get('reference_id')
        if not self.reference_id:
            raise http.Http404
        self.facade = Facade(self.reference_id)
        order_details_response = self.facade.set_order_details(str(self.request.basket.total_incl_tax))
        return super(PaymentDetailsView, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        # Add bankcard form to the template context
        ctx = super(PaymentDetailsView, self).get_context_data(**kwargs)
        ctx['seller_id'] = settings.AMAZON_PAYMENTS_SELLER_ID
        reference_id = self.request.GET.get('reference_id', None)
        if reference_id is None:
            raise http.Http404
        ctx['amazon_order_reference_id'] = reference_id
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


class ShippingAddressView(generic.TemplateView):
    template_name = 'checkout/shipping_address.html'

    def get_context_data(self, *args, **kwargs):
        ctx = super(ShippingAddressView, self).get_context_data(*args, **kwargs)
        ctx['seller_id'] = settings.AMAZON_PAYMENTS_SELLER_ID
        reference_id = self.request.GET.get('reference_id', None)
        if reference_id is None:
            raise http.Http404
        ctx['amazon_order_reference_id'] = reference_id
        return ctx


class ShippingMethodView(OscarShippingMethodView):

    def get(self, request, *args, **kwargs):
        # These pre-conditions can't easily be factored out into the normal
        # pre-conditions as they do more than run a test and then raise an
        # exception if it fails.
        self.reference_id = self.request.GET.get('reference_id')
        if self.reference_id:
            facade = Facade(self.reference_id)
            address = facade.get_shipping_address()
            address_fields = model_to_dict(address)
            address_fields.pop("country", None)

            self.checkout_session.ship_to_new_address(address_fields)

        # Check that shipping is required at all
        if not request.basket.is_shipping_required():
            # No shipping required - we store a special code to indicate so.
            self.checkout_session.use_shipping_method(
                NoShippingRequired().code)
            return self.get_success_response()

        # Check that shipping address has been completed
        if not self.checkout_session.is_shipping_address_set():
            messages.error(request, _("Please choose a shipping address"))
            return http.HttpResponseRedirect(
                reverse('checkout:shipping-address'))

        # Save shipping methods as instance var as we need them both here
        # and when setting the context vars.
        self._methods = self.get_available_shipping_methods()
        if len(self._methods) == 0:
            # No shipping methods available for given address
            messages.warning(request, _(
                "Shipping is unavailable for your chosen address - please "
                "choose another"))
            return http.HttpResponseRedirect(
                reverse('checkout:shipping-address'))
        elif len(self._methods) == 1:
            # Only one shipping method - set this and redirect onto the next
            # step
            self.checkout_session.use_shipping_method(self._methods[0].code)
            return self.get_success_response()

        # Must be more than one available shipping method, we present them to
        # the user to make a choice.
        return super(ShippingMethodView, self).get(request, *args, **kwargs)

    def get_success_response(self):
        return http.HttpResponseRedirect('{}?reference_id={}'.format(reverse('checkout:payment-details'), self.reference_id))
