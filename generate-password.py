## Useful for generating the Django Secret Key and Database

import secrets

length = 52
chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!#$%^&*(-_=+)'

secret_key = ''.join(secrets.choice(chars) for i in range(length))

print(secret_key)