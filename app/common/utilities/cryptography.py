import os
import base64
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util import Counter

# Carrega as variáveis de ambiente do arquivo .env
from dotenv import load_dotenv
load_dotenv()

CONFIG_ENCRYPTION = {
    'algorithm': 'AES-256-CTR',
    'key': os.getenv('SECRET_ENCRYPTION').encode(),
    'encoding': 'hex',
    'iv_length': 16,
}

class Cryptography:
    @staticmethod
    def encrypt(text: str) -> str:
        iv = get_random_bytes(CONFIG_ENCRYPTION['iv_length']).hex()[0:16]
        print ("TEXT",text)
        print("IV",bytes(iv, "utf-8"))
        #bufferFrom = bytes.fromhex(iv)
        #print('bufferFrom',bufferFrom)
        #(algorithm: string, key: CipherKey, iv: BinaryLike | null, options?: internal.TransformOption
        #const cipher = crypto.createCipheriv(CONFIG_ENCRYPTION.algorithm, Buffer.from(CONFIG_ENCRYPTION.key), iv)
        #cipher = AES.new(key=CONFIG_ENCRYPTION['key'], mode=AES.MODE_CTR, nonce=iv)
        ctr_e = Counter.new(128, initial_value=int.from_bytes(bytes(iv, "utf-8"), 'big'))
        cipher = AES.new(CONFIG_ENCRYPTION['key'], AES.MODE_CTR, counter=ctr_e)     
        encrypted = cipher.encrypt(text.encode(CONFIG_ENCRYPTION['encoding']))
        return 'ok'
        #return iv.hex() + ":" + base64.b64encode(encrypted).decode(CONFIG_ENCRYPTION['encoding'])

    @staticmethod
    def decrypt(text: str) -> str:
        text_parts = text.split(":")
        iv = bytes.fromhex(text_parts[0])
        encrypted_text = base64.b64decode(text_parts[1])
        cipher = AES.new(CONFIG_ENCRYPTION['key'], AES.MODE_CTR, nonce=iv)
        decrypted = cipher.decrypt(encrypted_text)
        return decrypted.decode(CONFIG_ENCRYPTION['encoding'])

# Exemplo de uso:
encrypted_text = Cryptography.encrypt('Hello, world!')
#decrypted_text = Cryptography.decrypt(encrypted_text)
print(encrypted_text)
#print(decrypted_text)
