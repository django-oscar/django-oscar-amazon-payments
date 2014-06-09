from oscar.apps.basket.app import BasketApplication

from apps.basket import views


class OverriddenBasketApplication(BasketApplication):
    # Specify new view for payment details
    summary_view = views.BasketView


application = OverriddenBasketApplication()
