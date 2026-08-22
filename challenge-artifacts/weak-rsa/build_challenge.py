import random
from sympy import randprime, gcd, mod_inverse

# Deliberately small primes -- factorable by trial division or sympy.factorint
# in well under a minute.
p = randprime(10**6, 10**7)
q = randprime(10**6, 10**7)
while p == q:
    q = randprime(10**6, 10**7)

n = p * q
phi = (p - 1) * (q - 1)
e = 65537

assert gcd(e, phi) == 1
d = mod_inverse(e, phi)

# The "message" is a short secret number, not the full flag text --
# this keeps n small enough to stay genuinely factorable.
secret = random.randint(100000, 999999)
ciphertext = pow(secret, e, n)

print(f"p = {p}")
print(f"q = {q}")
print(f"n = {n}")
print(f"e = {e}")
print(f"d = {d}  (for verification only, not given to students)")
print(f"secret (m) = {secret}  (for verification only, not given to students)")
print(f"ciphertext (c) = {ciphertext}")
print()

# Verify decryption works
decrypted = pow(ciphertext, d, n)
print(f"Verification decode: {decrypted}")
print(f"Flag would be: CTF{{{decrypted}}}")
