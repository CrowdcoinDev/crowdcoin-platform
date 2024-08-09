import base64
import hashlib
import hmac
import json
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from django.conf import settings
from Crypto.PublicKey import RSA
import os
import logging


logger = logging.getLogger(__name__)

def load_keys():
    with open('whatsapp_bot/configs/private.pem', 'rb') as f:
        private_key = RSA.import_key(f.read(), passphrase=settings.FLOW_PASSPHRASE)
    with open('whatsapp_bot/configs/public.pem', 'rb') as f:
        public_key = RSA.importKey(f.read(), passphrase=settings.FLOW_PASSPHRASE)
    return private_key, public_key

_private_key, _public_key = load_keys()

def decrypt_request(encrypted_data):
    # Load the private key
    private_key = RSA.import_key(_private_key.export_key(), passphrase=settings.FLOW_PASSPHRASE)
    cipher_rsa = PKCS1_OAEP.new(private_key)
    
    # Decrypt the data
    decrypted_data = cipher_rsa.decrypt(base64.b64decode(encrypted_data))
    return json.loads(decrypted_data)




def load_keys():
    with open('whatsapp_bot/configs/private.pem', 'rb') as f:
        private_key = RSA.import_key(f.read(), passphrase=settings.FLOW_PASSPHRASE)
    with open('whatsapp_bot/configs/public.pem', 'rb') as f:
        public_key = RSA.import_key(f.read(), passphrase=settings.FLOW_PASSPHRASE)
    return private_key, public_key

_private_key, _public_key = load_keys()

def decrypt_request(encrypted_data):
    try:
        # Ensure that the encrypted_data is correctly base64 encoded
        encrypted_data = base64.b64decode(encrypted_data)
        
        # Load the private key
        private_key = RSA.import_key(_private_key.export_key())
        cipher_rsa = PKCS1_OAEP.new(private_key)
        
        # Decrypt the data
        decrypted_data = cipher_rsa.decrypt(encrypted_data)
        
        return json.loads(decrypted_data)
    
    except ValueError as e:
        logger.error(f"Decryption error: {e}")
        raise ValueError("Decryption failed. Incorrect ciphertext length or format.")
    except Exception as e:
        logger.error(f"Unexpected error during decryption: {e}")
        raise


def encrypt_response(response_data):
    # Load the private key
    private_key = RSA.import_key(_private_key.export_key(), passphrase=settings.FLOW_PASSPHRASE)
    cipher_rsa = PKCS1_OAEP.new(private_key)
    
    # Encrypt the data
    encrypted_data = base64.b64encode(cipher_rsa.encrypt(json.dumps(response_data).encode('utf-8')))
    return encrypted_data

def verify_signature(request, signature, public_key):
    h = SHA256.new(request.body)
    try:
        pkcs1_15.new(public_key).verify(h, base64.b64decode(signature))
        return True
    except (ValueError, TypeError):
        return False
