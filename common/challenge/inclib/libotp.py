# -*- coding: utf-8 -*-
import time
import hmac
import hashlib
__all__ = ['OTP']
__author__ = 'opencTM'
__version__ = '1.1.0'  # modify_count.function_count.bug_count
__license__ = 'MIF'


class OTP(object):
    """ RFC 6238:   https://tools.ietf.org/html/rfc6287
                    HOTP = Truncate(HMAC-SHA-1(K, C))
                    TOTP = Truncate(HMAC-SHA-1(K, (T - T0) / X))
                    K   共享密钥(令牌种子)
                    C   计数器
                    T   代表当前时间整数(以UTC时间为标准)
                    T0  代表一个时间点整数,一般为0
                    X   口令变化周期,单位为秒,30秒或者60秒
                    Truncate HAMC算法得出的位值数比较多,通过length截断成一组不太长十进制数(例如6位数)
    """

    def __init__(self, length=6, timeout=30):
        self.T0 = 0L
        self.COUNT = 0L
        self.LENGTH = length
        self.TIMEOUT = timeout
        self.DIGITS_POWER = [long(10 ** i) for i in range(0, length + 1)]
        self.CHALLENGE = self.generate_challenge(str("%.9f" % time.time()).rjust(32, "0"))

    def __generate__(self, key, steps, hashtype):
        """ RFC 2104, RFC 4231 """
        hash = hmac.new(key, steps, hashtype).hexdigest()
        hash_bytes = [hash[i:i + 2] for i in range(0, len(hash), 2)]

        offset = int(hash_bytes[len(hash_bytes) - 1], 16) & 0xf
        binary = (((int(hash_bytes[offset], 16) & 0x7f) << 24) |
                  ((int(hash_bytes[offset + 1], 16) & 0xff) << 16) |
                  ((int(hash_bytes[offset + 2], 16) & 0xff) << 8) |
                  (int(hash_bytes[offset + 3], 16) & 0xff))

        otp = binary % self.DIGITS_POWER[self.LENGTH]
        result = str(otp).rjust(self.LENGTH, "0")
        return result

    def generate_hotp(self, key):
        steps = str(self.COUNT).rjust(16, "0")
        self.COUNT += 1
        return dict(SHA1=self.__generate__(key, steps, hashlib.sha1),
                    SHA256=self.__generate__(key, steps, hashlib.sha256),
                    SHA512=self.__generate__(key, steps, hashlib.sha512))

    def generate_totp(self, key):
        ts = (long(time.time()) - self.T0) / self.TIMEOUT
        steps = str(ts).rjust(16, "0")
        return dict(SHA1=self.__generate__(key, steps, hashlib.sha1),
                    SHA256=self.__generate__(key, steps, hashlib.sha256),
                    SHA512=self.__generate__(key, steps, hashlib.sha512))

    def generate_challenge(self, key):
        if not hasattr(self, 'CHALLENGE'):
            steps = str(long(time.time()) - self.T0).rjust(16, "0")
            self.CHALLENGE = dict(SHA1=self.__generate__(key, steps, hashlib.sha1),
                                  SHA256=self.__generate__(key, steps, hashlib.sha256),
                                  SHA512=self.__generate__(key, steps, hashlib.sha512))
            return self.CHALLENGE
        self.CHALLENGE = dict(SHA1=self.__generate__(key, str(self.CHALLENGE.get('SHA1')).rjust(16, "0"), hashlib.sha1),
                              SHA256=self.__generate__(key, str(self.CHALLENGE.get('SHA256')).rjust(16, "0"), hashlib.sha256),
                              SHA512=self.__generate__(key, str(self.CHALLENGE.get('SHA512')).rjust(16, "0"), hashlib.sha512))
        return self.CHALLENGE


if __name__ == '__main__':
    import uuid
    from datetime import datetime

    seed = uuid.uuid5(uuid.NAMESPACE_OID, uuid.NAMESPACE_OID.get_hex()).get_hex()
    otp = OTP(length=8, timeout=30)

    print "UTC:      ", datetime.strftime(datetime.utcfromtimestamp(long(time.time())), "%Y-%m-%d %H:%M:%S")
    print "TOTP:     ", otp.generate_totp(seed)

    for i in xrange(0, 5):
        print "HOTP:     ", otp.generate_hotp(seed)

    print "CHALLENGE:", otp.generate_challenge(seed)
    print "CHALLENGE:", otp.generate_challenge(seed)
    print "CHALLENGE:", otp.generate_challenge(seed)
