# utils.py
from cryptography.fernet import Fernet
from decouple import config

fernet = Fernet(config('FERNET_KEY'))


def encrypt_id(input_id):
    id_bytes = str(input_id).encode()
    return fernet.encrypt(id_bytes).decode()  # Return as string


def decrypt_id(encrypted_id):
    decrypted_id = fernet.decrypt(encrypted_id.encode())
    return int(decrypted_id.decode())


def decrypt_id_str(encrypted_id):
    decrypted_id = fernet.decrypt(encrypted_id.encode())
    return str(decrypted_id.decode())


