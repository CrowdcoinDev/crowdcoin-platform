import json
from base64 import b64decode, b64encode
from Crypto.PublicKey import RSA
from cryptography.hazmat.primitives.asymmetric.padding import OAEP, MGF1, hashes
from cryptography.hazmat.primitives.ciphers import algorithms, Cipher, modes
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from django.conf import settings
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

def decrypt_request(encrypted_flow_data_b64, encrypted_aes_key_b64, initial_vector_b64):
    try:
        # Decode the base64-encoded strings
        breakpoint()
        flow_data = b64decode(encrypted_flow_data_b64)
        iv = b64decode(initial_vector_b64)
        encrypted_aes_key = b64decode(encrypted_aes_key_b64)

        # Load the RSA private key
        private_key = _private_key


        # Decrypt the AES key using RSA
        aes_key = private_key.decrypt(encrypted_aes_key, OAEP(mgf=MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))

        # Decrypt the flow data using AES GCM mode
        encrypted_flow_data_body = flow_data[:-16]
        encrypted_flow_data_tag = flow_data[-16:]
        decryptor = Cipher(algorithms.AES(aes_key), modes.GCM(iv, encrypted_flow_data_tag)).decryptor()
        decrypted_data_bytes = decryptor.update(encrypted_flow_data_body) + decryptor.finalize()

        # Parse and return the decrypted JSON data
        decrypted_data = json.loads(decrypted_data_bytes.decode("utf-8"))
        return decrypted_data, aes_key, iv

    except Exception as e:
        print(f"Decryption error: {e}")
        raise

def encrypt_response(response, aes_key, iv):
    try:
        # Flip the initialization vector for encryption (if required by your protocol)
        flipped_iv = bytearray()
        for byte in iv:
            flipped_iv.append(byte ^ 0xFF)

        # Encrypt the response data using AES GCM mode
        encryptor = Cipher(algorithms.AES(aes_key), modes.GCM(flipped_iv)).encryptor()
        encrypted_data = encryptor.update(json.dumps(response).encode("utf-8")) + encryptor.finalize()

        # Concatenate the encrypted data with the GCM tag and encode as base64
        return b64encode(encrypted_data + encryptor.tag).decode("utf-8")

    except Exception as e:
        print(f"Encryption error: {e}")
        raise
def verify_signature(request, signature, public_key):
    h = SHA256.new(request.body)
    try:
        pkcs1_15.new(public_key).verify(h, base64.b64decode(signature))
        return True
    except (ValueError, TypeError):
        return False
