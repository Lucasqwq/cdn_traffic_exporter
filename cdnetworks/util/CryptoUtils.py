import hashlib
import hmac
from binascii import hexlify


class CryptoUtils:
    @staticmethod
    def sha256_hex(s):
        """
        hmac+sha256+hex
        """
        md = hashlib.sha256()
        md.update(s.encode('utf-8'))
        d = md.digest()
        return hexlify(d).decode('utf-8').lower()

    @staticmethod
    def hmac256(key, msg):
        """
        hmac+sha256
        """
        mac = hmac.new(key, msg.encode('utf-8'), hashlib.sha256)
        return mac.digest()
