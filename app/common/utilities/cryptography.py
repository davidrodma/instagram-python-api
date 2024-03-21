import os
import base64
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

# Carrega as variáveis de ambiente do arquivo .env
from dotenv import load_dotenv
load_dotenv()

CONFIG_ENCRYPTION = {
    'algorithm': 'AES',
    'key': os.getenv('SECRET_ENCRYPTION').encode(),
    'encoding': 'utf-8',
    'iv_length': 16,
}

class Cryptography:
    @staticmethod
    def encrypt(text: str) -> str:
        iv = get_random_bytes(CONFIG_ENCRYPTION['iv_length'])
        cipher = AES.new(CONFIG_ENCRYPTION['key'], AES.MODE_CFB, iv)
        encrypted = cipher.encrypt(text.encode())
        return base64.b64encode(iv + encrypted).decode(CONFIG_ENCRYPTION['encoding'])

    @staticmethod
    def decrypt(text: str) -> str:
        text = base64.b64decode(text.encode(CONFIG_ENCRYPTION['encoding']))
        iv = text[:CONFIG_ENCRYPTION['iv_length']]
        encrypted = text[CONFIG_ENCRYPTION['iv_length']:]
        cipher = AES.new(CONFIG_ENCRYPTION['key'], AES.MODE_CFB, iv)
        decrypted = cipher.decrypt(encrypted)
        return decrypted.decode(CONFIG_ENCRYPTION['encoding'])