# -*- coding: utf-8 -*-
import sys
from hashlib import md5
from inclib.libotp import OTP
from inclib.stdio import Const
from inclib.stdio import Define


class _Secret(object):
    @staticmethod
    def memfrob(text):
        if isinstance(text, str):
            return ''.join([chr(ord(t) ^ 42) for t in text])
        return

    @staticmethod
    def md5_hash(text):
        if isinstance(text, str):
            m = md5()
            m.update(text)
            return m.hexdigest()
        return

    @classmethod
    def get_seed(cls, key):
        """ generic secret by gate-coreshell """
        c = Const(SEED=Define(str(key).upper()))
        serial = ''.join(['='.join([str(k), str(c(k).value)]) for k in c])
        secret = cls.memfrob(serial).encode('hex')
        codes = Define(cls.md5_hash(secret)).value
        return codes


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(1)

    otp = OTP(length=8, timeout=120)
    otp.CHALLENGE = dict(SHA1=sys.argv[1], SHA256=sys.argv[1], SHA512=sys.argv[1])
    print {'TEST': otp.generate_challenge(_Secret.get_seed(_Secret.memfrob('46454d4344'.decode('hex'))))}
    otp = None
