from base64 import b64decode, b64encode
from cryptography.hazmat.primitives.asymmetric.padding import OAEP, MGF1
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import algorithms, Cipher, modes
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key

import json
import logging

logger = logging.getLogger(__name__)

def load_keys():
    # Load the private key
    with open('whatsapp_bot/configs/private.pem', 'rb') as f:
        private_key = load_pem_private_key(f.read(), password=b'passphrase')
    
    # Load the public key
    with open('whatsapp_bot/configs/public.pem', 'rb') as f:
        public_key = load_pem_public_key(f.read())  # Correct method for loading public keys
    
    return private_key, public_key

_private_key, _public_key = load_keys()

def decrypt_request(encrypted_flow_data_b64, encrypted_aes_key_b64, initial_vector_b64):
    try:
        # Decode the base64-encoded strings
        flow_data = b64decode(encrypted_flow_data_b64)
        iv = b64decode(initial_vector_b64)
        encrypted_aes_key = b64decode(encrypted_aes_key_b64)

        # Decrypt the AES key using RSA with OAEP padding
        aes_key = _private_key.decrypt(
            encrypted_aes_key,
            OAEP(
                mgf=MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        # Decrypt the flow data using AES GCM mode
        encrypted_flow_data_body = flow_data[:-16]
        encrypted_flow_data_tag = flow_data[-16:]
        decryptor = Cipher(algorithms.AES(aes_key), modes.GCM(iv, encrypted_flow_data_tag)).decryptor()
        decrypted_data_bytes = decryptor.update(encrypted_flow_data_body) + decryptor.finalize()

        # Parse and return the decrypted JSON data
        decrypted_data = json.loads(decrypted_data_bytes.decode("utf-8"))
        return decrypted_data, aes_key, iv

    except Exception as e:
        logger.error(f"Decryption error: {e}")
        raise

def encrypt_response(response, aes_key, iv):
    try:
        # Convert response to bytes
        response_bytes = json.dumps(response).encode('utf-8')

        # Encrypt the response
        encryptor = Cipher(algorithms.AES(aes_key), modes.GCM(iv)).encryptor()
        ciphertext = encryptor.update(response_bytes) + encryptor.finalize()

        # Append the GCM tag to the ciphertext
        ciphertext_with_tag = ciphertext + encryptor.tag

        # Encode the ciphertext in base64
        encrypted_response_b64 = b64encode(ciphertext_with_tag).decode('utf-8')
        return encrypted_response_b64

    except Exception as e:
        logger.error(f"Encryption error: {e}")
        raise
