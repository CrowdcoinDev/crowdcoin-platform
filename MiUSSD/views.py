import logging
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .models import Campaign, Node, Interaction

logger = logging.getLogger(__name__)
User = get_user_model()

class UssdHandler:
    def __init__(self, request):
        self.request = request
        self.msisdn = self.format_msisdn(request.GET.get('ussd_msisdn'))
        self.ussd_number = request.GET.get('ussd_request')  # USSD number passed by the proxy
        self.campaign = get_object_or_404(Campaign, ussd_number=self.ussd_number)
        self.user, _ = User.objects.get_or_create(username=self.msisdn)
        self.session = request.session
        self.session_data = self.session.get('session_data', {})
        self.node_name = '' #self.campaign.starting_node.name #self.session_data.get('node_name', self.campaign.starting_node.name)

    def format_msisdn(self, msisdn):
        return '0' + str(msisdn[2:])

    def set_node(self, node_name):
        self.session_data['node_name'] = node_name
        self.session['session_data'] = self.session_data

    def get_node(self):
        if self.node_name:
            return get_object_or_404(Node, name=self.node_name, campaign=self.campaign)
        return self.campaign.starting_node

    def handle_node(self, node):
        logger.debug(f"Handling node {node.name}")
        user_response_key = f"ussd_response_{node.name}"
        user_response = self.request.GET.get(user_response_key)
        response = node.get_response(self.request, user_response)

        # Log interaction
        Interaction.objects.create(
            user=self.user,
            node=node,
            response=user_response or '',
            session_data=dict(self.session)
        )

        # Determine if session should continue or end
        if node.session_end:
            self.session.flush()  # Clear session data if session ends
        else:
            if node.responses.filter(user_response=user_response).exists():
                next_node = node.responses.get(user_response=user_response).next_node
                self.set_node(next_node.name)
                return self.handle_node(next_node)

        return HttpResponse(response)

    def process_request(self):
        try:
            # Authenticate user or prompt registration
            if not self.user.is_authenticated:
                if 'register' not in self.session_data:
                    self.session_data['register'] = True
                    self.session['session_data'] = self.session_data
                    return HttpResponse("Please register to continue.")

            current_node = self.get_node()
            return self.handle_node(current_node)
        except Exception as e:
            logger.exception(e)
            response = "An error occurred. Please contact support\n0) Menu"
            return HttpResponse(response)

def ussd_view(request):
    handler = UssdHandler(request)
    return handler.process_request()
