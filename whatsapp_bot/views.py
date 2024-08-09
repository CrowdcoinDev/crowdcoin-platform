from django.http import JsonResponse, HttpResponse
from django.views import View
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from .utils import decrypt_request, encrypt_response
from .models import UserInteraction, ResponseTemplate, Flow, FlowStep

import json
import requests
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

COMMANDS = {
    '/download': {
        'description': 'Downloads files',
        'usage': '/download URL',
        'function': 'download_file',
        'template': 'download_file'
    },
    '/exchange': {
        'description': 'Exchange Voucher',
        'usage': '/exchange DATA',
        'function': 'exchange_voucher',
        'template': 'exchange_voucher'
    }
}

@method_decorator(csrf_exempt, name='dispatch')
class WebhookView(View):
    def get(self, request, *args, **kwargs):
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')

        if mode == 'subscribe' and token == settings.WEBHOOK_VERIFY_TOKEN:
            return HttpResponse(challenge, status=200)
        else:
            return HttpResponse(status=403)

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body.decode('utf-8'))
            logger.info(data)
            message = data.get('entry', [{}])[0].get('changes', [{}])[0].get('value', {}).get('messages', [{}])[0]

            if message and message.get('type') == 'text':
                businessPhoneNumberId = data.get('entry', [{}])[0].get('changes', [{}])[0].get('value', {}).get('metadata', {}).get('phone_number_id')
                businessPhoneNumberDisplay = data.get('entry', [{}])[0].get('changes', [{}])[0].get('value', {}).get('metadata', {}).get('display_phone_number')
                profileName = data.get('entry', [{}])[0].get('changes', [{}])[0].get('value', {}).get('contacts', [{}])[0].get('profile', {}).get('name')

                response = self.handle_message(message, businessPhoneNumberId, profileName, businessPhoneNumberDisplay)
                return JsonResponse({'status': 'success', 'response': response}, status=200)
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid message format'}, status=400)
        except Exception as e:
            logger.exception(e)
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)

    def handle_message(self, message, businessPhoneNumberId, profileName, businessPhoneNumberDisplay, *args, **kwargs):
        phone_number = message.get('from')
        text = message.get('text', {}).get('body', '').strip().lower()
        is_template = False

        # Check if the user exists
        user = User.objects.filter(username=phone_number).first()
        context = locals()
        if not user:
            response_message = "signup"
            is_template = True
            # return self.send_response_via_whatsapp(phone_number, None, businessPhoneNumberId,"signup",context)
        else:
            # Process the command or the default action
            command_prefix = text.split(' ')[0]
            command_argument = ' '.join(text.split(' ')[1:])
            response_message = "Default response."

            if command_prefix in COMMANDS:
                try:
                    command_function = COMMANDS[command_prefix]['function']
                    response_message = globals()[command_function](command_argument, phone_number, businessPhoneNumberId, businessPhoneNumberDisplay)
                except Exception as e:
                    logger.exception(e)
                    response_message = "Error processing command."
            else:
                response_message = "Invalid command. Try again."

        # Store the interaction
        UserInteraction.objects.create(
            user=user if user else None,
            phone_number=phone_number,
            message=text,
            response=response_message
        )

        # Send the response via WhatsApp API
        if is_template:
            self.send_response_via_whatsapp(phone_number, None, businessPhoneNumberId, response_message,context)
        else:
            self.send_response_via_whatsapp(phone_number, response_message, businessPhoneNumberId)

        return response_message

    def send_response_via_whatsapp(self, phone_number, response_message, businessPhoneNumberId=None, template_name=None, context=None):
        # Fetch the template from the database if a template name is provided
        if template_name:
            template = ResponseTemplate.objects.get(name=template_name)
            data = template.render(context or {})
        else:
            # Default message structure if no template is used
            data = {
                "messaging_product": "whatsapp",
                "to": phone_number,
                "text": {"body": response_message}
            }

        url = f"https://graph.facebook.com/v18.0/{businessPhoneNumberId}/messages"
        headers = {
            "Authorization": f"Bearer {settings.GRAPH_API_TOKEN}",
            "Content-Type": "application/json"
        }

        if settings.PRODUCTION:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code != 200:
                logger.warning(f"Failed to send message: {response.status_code}, {response.text}")
        else:
            logger.info(f"Sent message: {data}")

@method_decorator(csrf_exempt, name='dispatch')
class FlowView(View):
    def post(self, request, *args, **kwargs):
        try:
            logger.info(request.body)
            breakpoint()
            encrypted_data =  json.loads(request.body).get('encrypted_flow_data')
            decrypted_body = decrypt_request(encrypted_data)
            
            # Determine the next screen/action based on the decrypted body
            response_data = self.get_next_screen(decrypted_body)
            
            # Encrypt the response data
            encrypted_response = encrypt_response(response_data)
            
            return HttpResponse(encrypted_response, content_type='application/json')
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    def get_next_screen(self, decrypted_body):
        action = decrypted_body.get('action')
        if action == "ping":
            return {'data': {'status': 'active'}}
        elif action == "INIT":
            return {'screen': 'MY_SCREEN', 'data': {'greeting': 'Hey there! 👋'}}
        elif action == "data_exchange":
            # Handle data exchange based on the current screen
            screen = decrypted_body.get('screen')
            if screen == 'MY_SCREEN':
                # Example: Update data or process interactions here
                return {'screen': 'NEXT_SCREEN', 'data': {'confirmation': 'Data received!'}}
        else:
            return {'data': {'error': 'Unknown action'}}

        return {'data': {'error': 'Invalid request'}}        

    def handle_signup(self, phone_number):
        """
        Handles the signup process if the user is not found.
        """
        signup_template = ResponseTemplate.objects.filter(name='signup').first()
        context = {'phone_number': phone_number}
        rendered_signup = signup_template.render(context) if signup_template else "Please sign up to continue."
        
        # Optionally store the interaction even for signup prompts
        UserInteraction.objects.create(
            phone_number=phone_number,
            message="Signup Prompt",
            response=rendered_signup
        )
        
        return JsonResponse({"message": rendered_signup}, status=200)

