# backend/whatsapp_integration.py

import requests
from django.conf import settings
import mimetypes
from requests_toolbelt.multipart.encoder import MultipartEncoder
from urllib import quote


def construct_whatsapp_url(phone_number, command):
    encoded_command = quote(command)
    whatsapp_url = "https://wa.me/{phone_number}?text={encoded_command}".format(phone_number,encoded_command)
    return whatsapp_url

# Example usage
# phone_number = "27692734500"
# command = "/download https://example.com/file.zip"
# whatsapp_url = construct_whatsapp_url(phone_number, command)
# print(whatsapp_url)

def send_whatsapp_file(phone_number, file_path, file_type, businessPhoneNumberId):
    try:
        # Example: Using requests to send a WhatsApp message with file
        url = "https://graph.facebook.com/v18.0/{businessPhoneNumberId}/media".format(businessPhoneNumberId)

        headers = {
            "Authorization": "Bearer {settings.GRAPH_API_TOKEN}".format(settings.GRAPH_API_TOKEN)
        }

        
        # Determine content type based on file extension
        content_type, _ = mimetypes.guess_type(file_path)
        if not content_type or content_type in ['text/markdown']:
            content_type = 'text/plain'
            # raise ValueError(f"Cannot determine content type for file: {file_path}")


        # Prepare the multipart form data
        encoder = MultipartEncoder(
            fields={
                'file': (file_path, open(file_path, 'rb'), content_type),
                'type': file_type,
                'messaging_product': 'whatsapp'
            }
        )

        headers['Content-Type'] = encoder.content_type

        # Send the request
        response = requests.post(url, headers=headers, data=encoder)

        response.raise_for_status()

        media_id = response.json().get('id')

        headers['Content-Type'] = "application/json"
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": 'document',
            'document': {
                "id": media_id,
                "caption":file_type,
                "filename":file_path.split('/')[-1]
            }
        }
        # payload = {
        #     "messaging_product": "whatsapp",
        #     "to": phone_number,
        #     "type": file_type,
        #     file_type: {"id": media_id}
        # }

        # Send message with media id
        response = requests.post(
            "https://graph.facebook.com/v18.0/{businessPhoneNumberId}/messages".format(businessPhoneNumberId),
            headers=headers,
            json=payload
        )
        response.raise_for_status()

        print("WhatsApp message sent with file: {file_path}".format(file_path))

    except requests.exceptions.RequestException as e:
        print("Error sending WhatsApp message: {e}".format(e))
