from django.urls import include, path, re_path
from django.contrib.auth import views as auth_views
from django.contrib import admin
from website.views import *
from django.conf.urls.static import static
from django.views.static import serve as static_serve
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from tastypie.api import Api
from website.api.resources import *
from website.ussd import ussd_view

admin.autodiscover()
admin.site.site_header = 'Crowdcoin Dashboard'

api_prefix = "api/v1/"
v1_api = Api(api_name='v1')
v1_api.register(UserProfileResource())
v1_api.register(CreateUserResource())
v1_api.register(UserResource())
v1_api.register(SimCardResource())
v1_api.register(NetworkResource())
v1_api.register(UniqueIdentifierResource())
v1_api.register(AirtimeDepositLeadResource())
v1_api.register(PocketResource())
v1_api.register(TransactionResource())
v1_api.register(CrowdcoinPaymentLeadResource())
v1_api.register(BankPaymentLeadResource())
v1_api.register(BankDepositLeadResource())
v1_api.register(SmsInboundResource())
v1_api.register(VoucherResource())
v1_api.register(VoucherExchangeLeadResource())
v1_api.register(VoucherPaymentLeadResource())
v1_api.register(VoucherProviderResource())
v1_api.register(MerchantResource())
v1_api.register(PromotionResource())
v1_api.register(ClaimedPromotionResource())
v1_api.register(SmsOutBoundResource())

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(v1_api.urls)),
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path(f'{api_prefix}whatsapp/', include('whatsapp_bot.urls')),
    re_path(r'^static/(?P<path>.*)$', static_serve, {'document_root': settings.STATIC_ROOT}),
    re_path(r'^media/(?P<file_path>.*)', MediaView),
    path(f'{api_prefix}support_ticket_create/', support_ticket_create),
    path(f'{api_prefix}smsinbound', SmsInboundView, name='smsinbound'),
    path(f'{api_prefix}create_transaction/', create_funds_transaction_api),
    path(f'{api_prefix}reset_password/', reset_password),
    path(f'{api_prefix}deposit_lead/', api_generate_deposit_lead),
    path(f'{api_prefix}export/', export_funds_csv),
    path(f'{api_prefix}login/', api_login),
    path(f'{api_prefix}register_merchant/', api_merchant_registration),
    path(f'{api_prefix}ussd/', ussd_view, name='ussd'),
    path(f'{api_prefix}otp/', get_otp_view, name='get_otp'),
    path('loaderio-b193a2f576f0426fef58ef4dbe597971/', loaderio),
    # path('sso/', include('freshdesk.urls')),
    path('', LandingView, name="landing"),
] + staticfiles_urlpatterns() + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
