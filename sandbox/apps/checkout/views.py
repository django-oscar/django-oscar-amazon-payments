from django import http
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.conf import settings
from django.utils.translation import ugettext as _
from django.views import generic
from django.forms.models import model_to_dict

from oscar.apps.checkout.views import PaymentDetailsView as OscarPaymentDetailsView
from oscar.apps.checkout.views import ShippingMethodView as OscarShippingMethodView

from oscar_amazon_payments.facade import Facade


class PaymentDetailsView(OscarPaymentDetailsView):

    def get(self, *args, **kwargs):
        self.reference_id = self.request.GET.get('reference_id')
        if not self.reference_id:
            return http.HttpBadRequest()
        self.facade = Facade(self.reference_id)
        if not self.preview:
            order_details_response = self.facade.set_order_details(str(self.request.basket.total_incl_tax))
        return super(PaymentDetailsView, self).get(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        # Posting to payment-details isn't the right thing to do.  Form
        # submissions should use the preview URL.
        if not self.preview:
            return http.HttpBadRequest()
        if request.POST.get('action', '') == 'place_order':
            return self.handle_place_order_submission(request)
        else:
            return http.HttpBadRequest()

    def get_context_data(self, **kwargs):
        # Add bankcard form to the template context
        ctx = super(PaymentDetailsView, self).get_context_data(**kwargs)
        ctx['seller_id'] = settings.AMAZON_PAYMENTS_SELLER_ID
        reference_id = self.request.GET.get('reference_id', None)
        if reference_id is None:
            raise http.Http404
        ctx['amazon_order_reference_id'] = reference_id
        return ctx

    def handle_place_order_submission(self, request):
        self.reference_id = self.request.GET.get('reference_id')
        if not self.reference_id:
            return http.HttpBadRequest()
        self.facade = Facade(self.reference_id)
        confirm_order_response = self.facade.confirm_order_details()
        return self.facade.fulfill_transaction(self.request.basket.total_incl_tax, settings.AMAZON_PAYMENTS_CURRENCY)


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
            address = facade.get_partial_shipping_address()
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
