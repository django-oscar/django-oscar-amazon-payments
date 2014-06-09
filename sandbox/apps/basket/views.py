from django.conf import settings
from oscar.apps.basket.views import BasketView as OscarBasketView


class BasketView(OscarBasketView):

    def get_context_data(self, *args, **kwargs):
        ctx = super(BasketView, self).get_context_data(*args, **kwargs)
        ctx['seller_id'] = settings.AMAZON_SELLER_ID
        return ctx
