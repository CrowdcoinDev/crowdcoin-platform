from django.http import JsonResponse, HttpResponse
from django.views import View
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json
import requests
from .models import Conversation
from .commands import download_file, exchange_voucher

COMMANDS = {
    '': {
        'description': 'Default: Search for Podcast',
        'usage': 'keyword',
        'function': download_file
    },
    '/download': {
        'description': 'Downloads files',
        'usage': '/download URL',
        'function': download_file
    },
    '/exchange': {
        'description': 'Exchange Voucher',
        'usage': '/exchange DATA',
        'function': exchange_voucher
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
            # import pdb; pdb.set_trace()
            data = json.loads(request.body.decode('utf-8'))
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
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)

    def handle_message(self, message, businessPhoneNumberId, profileName, businessPhoneNumberDisplay):
        phone_number = message.get('from')
        text = message.get('text', {}).get('body', '').strip().lower()
        if text:
            command_prefix = text.split(' ')[0]
            command_argument = ' '.join(text.split(' ')[1:])
            response_message = COMMANDS['']['function'](text, phone_number, businessPhoneNumberId, businessPhoneNumberDisplay)

            if command_prefix in COMMANDS:
                try:
                    response_message = COMMANDS[command_prefix]['function'](command_argument, phone_number, businessPhoneNumberId, businessPhoneNumberDisplay)
                except Exception as e:
                    response_message = "Error processing command: "
            else:
                available_commands = '\n'
                # import pdb; pdb.set_trace()
                for cmd,info in COMMANDS.items():
                    available_commands += "*{cmd}* \n {description} \n Usage: `{usage}`\n\n".format(cmd=cmd, description=info['description'], usage=info['usage'])
                response_message = "Try one of the following commands"+available_commands

            # Save the conversation
            conversation, created = Conversation.objects.get_or_create(phone_number=phone_number)

            # if not conversation.messages:
            #     conversation.messages = []

            # conversation.messages.append({'message': text, 'response': response_message})
            conversation.save()

            # Implement logic to send the response via WhatsApp API
            self.send_response_via_whatsapp(phone_number, response_message, businessPhoneNumberId)

            return response_message
        else:
            return "Invalid request"

    def send_response_via_whatsapp(self, phone_number, response_message, businessPhoneNumberId):
        # Implement the logic to send the response message via the WhatsApp API
        url = "https://graph.facebook.com/v18.0/{businessPhoneNumberId}/messages".format(businessPhoneNumberId=businessPhoneNumberId)
        headers = {
            "Authorization": "Bearer {GRAPH_API_TOKEN}".format(GRAPH_API_TOKEN=settings.GRAPH_API_TOKEN),
            "Content-Type": "application/json"
        }
        data = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "text": {"body": response_message}
        }
        # import pdb; pdb.set_trace()
        response = requests.post(url, headers=headers, json=data)
        if response.status_code != 200:
            print("Failed to send message: {response.status_code}, {response.text}".format(response.status_code,response.text))

# Other views can be here...
