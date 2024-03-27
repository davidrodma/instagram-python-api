import os
import base64
from Crypto.Cipher import AES
from Crypto.Util import Counter

# Chave de 64 bytes em hexadecimal (32 bytes)
key_hex = b'0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef'
print('key_hex',key_hex)
# Converte a chave hexa para bytes
key_bytes = bytes.fromhex(key_hex.decode())
print('key_bytes',key_bytes)

# Cria o contador para o modo CTR
ctr = Counter.new(128)

# Cria o cifrador AES com a chave e o contador especificados
cipher = AES.new(key_bytes, AES.MODE_CTR, counter=ctr)

# Texto a ser criptografado
plaintext = b'Hello, world!'

# Criptografa o texto
ciphertext = cipher.encrypt(plaintext)

# Exibe o texto criptografado
print("Texto criptografado:", base64.b64encode(ciphertext).decode())
