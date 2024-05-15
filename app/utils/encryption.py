from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64

from app.config import settings

key = settings.ACCESS_TOKEN_SECRET_KEY.encode('utf-8').ljust(32)[:32]


def encrypt_string(plain_text):
    cipher = AES.new(key, AES.MODE_CBC)
    padded_text = pad(plain_text.encode('utf-8'), AES.block_size)
    cipher_text = cipher.encrypt(padded_text)
    return base64.b64encode(cipher.iv + cipher_text).decode('utf-8')


def decrypt_string(encrypted_text):
    encrypted_data = base64.b64decode(encrypted_text)
    iv = encrypted_data[:AES.block_size]
    cipher_text = encrypted_data[AES.block_size:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plain_text = unpad(cipher.decrypt(cipher_text), AES.block_size)
    return plain_text.decode('utf-8')
