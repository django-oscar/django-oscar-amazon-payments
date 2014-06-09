from django.conf.urls import *
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static

from apps.app import shop

#from oscar_amazon_payments.dashboard.app import application

admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    # Include dashboard URLs
#    (r'^dashboard/amazon-payments/', include(application.urls)),
#    (r'^amazon-payments/', include('oscar_amazon_payments.urls')),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    (r'', include(shop.urls)),
)
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
