import logging
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.contrib.sessions.models import Session
from .models import User, UserProfile, Merchant, Transaction, VoucherPaymentLead
import secrets
import string

logger = logging.getLogger(__name__)

class UssdHandler:
    def __init__(self, request):
        self.request = request
        self.msisdn = self.format_msisdn(request.GET.get('ussd_msisdn'))
        self.node_name = request.GET.get('ussd_node_name','Menu')
        self.network = request.GET.get('ussd_network_name')
        self.ussd_request = request.GET.get('ussd_request')
        self.user, _ = User.objects.get_or_create(username=self.msisdn)
        self.user_profile, _ = UserProfile.objects.get_or_create(user=self.user, msisdn=self.user.username)
        self.session = request.session
        self.session['msisdn'] = self.msisdn

    def format_msisdn(self, msisdn):
        return '0' + str(msisdn[2:])

    def set_node(self, node_name):
        self.session['node_name'] = node_name

    def get_node(self):
        return self.session.get('node_name', self.node_name)

    def handle_menu(self):
        logger.debug("Called Menu")
        merchant_id, amount = None, None
        if self.ussd_request:
            try:
                ussd_request_args = self.ussd_request.strip("#").split(settings.CROWDCOIN_USSD_STRING[:-1], 1)[1][1:].split("*")
                merchant_id = int(ussd_request_args[0])
                amount = int(ussd_request_args[1])
            except Exception as e:
                logger.debug(e)

        if merchant_id and Merchant.objects.filter(id=merchant_id).exists():
            merchant = Merchant.objects.get(id=merchant_id)
            response = f"(((C) {merchant.trading_name} \n\n" \
                       f"You are about to pay R {amount} using airtime.\n" \
                       f"Please enter your reference:\n" \
                       f"Example: INV123\n\n" \
                       f"0. Help.\n"
            self.set_node('EnterReference')
        else:
            response = "(((C) Crowdcoin\n\n" \
                       "1. Balance\n" \
                       "2. Top Up\n" \
                       "3. History\n" \
                       "4. Reset Password\n" \
                       "0. Help\n"
        return HttpResponse(response)

    def handle_find_merchant_results(self):
        logger.debug("Called Find Merchant Results")
        keyword = self.request.GET.get("ussd_response_FindMerchantKeyword")
        merchants = Merchant.objects.filter(trading_name__icontains=keyword)
        if merchants.exists():
            merchants_string = "(((C) Merchants Found\n\n"
            for merchant in merchants:
                merchants_string += f"{merchant.id}={merchant.trading_name}\n"
            response = merchants_string
        else:
            response = "(((C) Crowdcoin\n\n" \
                       "Use of service subject to Ts & Cs available at http://www.crowdcoin.co.za/legals.\n\n" \
                       "7. Join Crowdcoin for Business"
        return HttpResponse(response)

    def handle_mini_statement(self):
        logger.debug("Called Mini Statement")
        profile = get_object_or_404(UserProfile, user__username=self.msisdn)
        pocket = profile.default_pocket
        transactions = Transaction.objects.filter(pocket=pocket, active=True).order_by('-datetime')[:10]
        transactions_string = "(((C) Mini Statement\n\n"
        for i, transaction in enumerate(transactions):
            tag = "-" if transaction.debit else "+"
            description = "No description"
            if transaction.identifiers.all().count() > 0:
                description = transaction.identifiers.all().last().value #.get(name='transaction_tag').value
                description = f'{description.split()[0]}...{description.split()[-1]}'
            transactions_string += f"{i+1}.{tag}R{transaction.amount} - {description}\n"
        response = transactions_string if transactions else "You have no transactions."
        return HttpResponse(response)

    def handle_balance(self):
        logger.debug(self.msisdn)
        profile = get_object_or_404(UserProfile, user__username=self.msisdn)
        pocket = profile.default_pocket
        response = f"(((C) {pocket.tag}\n\nBalance: R{pocket.balance()} "
        return HttpResponse(response)

    def handle_redeem_voucher(self):
        profile = get_object_or_404(UserProfile, user__username=self.msisdn)
        pocket_to = profile.default_pocket
        voucher_code = self.request.GET.get("ussd_response_Voucher_Code")
        voucher_provider = "Crowdcoin" if int(self.request.GET.get("ussd_response_Voucher_Provider")) == 1 else "Vodacom"

        if voucher_provider == 'Crowdcoin':
            voucher = get_object_or_404(VoucherPaymentLead, active=True, voucher_code=voucher_code)
            if voucher.status in ["Pending", "Awaiting Collection"]:
                voucher.pocket_to = pocket_to
                voucher.active = False
                voucher.status = "Collected"
                voucher.provider = voucher_provider
                voucher.save()
                response = f"Thank you!\n{voucher.amount} Crowdcoin credited to {voucher.pocket_to.tag}."
                self.send_sms(f"Hi {profile.user.get_short_name()}\n"
                              f"{pocket_to.tag} has been credited with {voucher.amount} Crowdcoins.\n"
                              f"Balance:{pocket_to.balance()}", profile.msisdn)
            else:
                response = "You have entered an incorrect Voucher Security Pin."
        else:
            voucher, _ = VoucherPaymentLead.objects.get_or_create(
                active=True,
                voucher_code=voucher_code,
                provider=voucher_provider,
                pocket_to=pocket_to
            )
            response = f"Please wait while we convert your {voucher_provider} voucher to a Crowdcoin voucher."
        return HttpResponse(response)

    def handle_generate_voucher(self):
        profile = get_object_or_404(UserProfile, user__username=self.msisdn)
        pocket_from = profile.default_pocket
        amount = float(self.request.GET.get("ussd_response_Voucher_Amount"))
        if pocket_from.balance() >= amount and amount > 0:
            voucher = VoucherPaymentLead.objects.create(
                active=True,
                pocket_from=pocket_from,
                amount=amount,
                sender_msisdn=self.msisdn,
                recipient_msisdn=self.msisdn,
                status='Awaiting Collection'
            )
            response = f"(((C) Voucher Details\n\n" \
                       f"Amount:{voucher.amount}\n" \
                       f"Voucher:{voucher.voucher_code}\n" \
                       f"Balance:{pocket_from.balance()} \n"
        else:
            response = f"Insufficient balance.\nAvailable Balance: {pocket_from.balance()}" if amount > 0 else "You entered an incorrect amount."
        return HttpResponse(response)

    def handle_reset_password(self):
        logger.debug("Called Reset Password")
        user = self.user
        alphabet = string.ascii_letters + string.digits
        new_password = ''.join(secrets.choice(alphabet) for _ in range(8))  # Generate an 8 character password
        user.set_password(new_password)
        user.save()
        response = f"Your password has been reset. Your new password is {new_password}. Please change it after logging in."
        return HttpResponse(response)

    def send_sms(self, message, msisdn):
        # Implement the SMS sending logic here
        pass

    def process_request(self):
        try:
            handlers = {
                "Menu": self.handle_menu,
                "FindMerchantResults": self.handle_find_merchant_results,
                "Mini_Statement": self.handle_mini_statement,
                "Balance": self.handle_balance,
                "Redeem_Voucher": self.handle_redeem_voucher,
                "Generate_Voucher": self.handle_generate_voucher,
                "Reset_Password": self.handle_reset_password  # Add this line
            }
            current_node = self.get_node()
            handler = handlers.get(current_node, lambda: HttpResponse("No option selected", status=200))
            return handler()
        except Exception as e:
            logger.exception(e)
            response = "An error occurred. Please contact support\n0) Menu"
            return HttpResponse(response)

def ussd_view(request):
    handler = UssdHandler(request)
    return handler.process_request()
