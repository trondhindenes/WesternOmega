#!/usr/bin/python
import sys
from passlib.hash import pbkdf2_sha256
import base64

password = sys.argv[1]
hash = pbkdf2_sha256.hash(password)
b64 = base64.b64encode(hash)
print(b64)

