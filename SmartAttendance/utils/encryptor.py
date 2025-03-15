
from utils.base64 import base64_encode, base64_decode

      
class SimpleEncryptor:
    def __init__(self, key_base64):
        self.key = base64_decode(key_base64) 

    def xor_encrypt(self, data):

        if isinstance(data, int):
            data = data.to_bytes(8, 'big') 

        encrypted = bytes(data[i] ^ self.key[i % len(self.key)] for i in range(len(data)))
        return encrypted

    def xor_decrypt(self, encrypted_data):
        
        decrypted = self.xor_encrypt(encrypted_data) 
        return int.from_bytes(decrypted, 'big')  

