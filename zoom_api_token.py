import jwt
import os
from time import time
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get('zoom_api_key')
api_sec = os.environ.get('zoom_api_sec')


def generate_token():
    token = jwt.encode(
        {'iss': api_key, 'exp': time() + 5000},
        api_sec,
        algorithm='HS256'
    )
    return token
