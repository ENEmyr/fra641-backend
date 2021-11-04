import time
from typing import Dict

import jwt

from configs import JWT_CONF


def token_response(token: str) -> dict:
    return {
        "access_token": token,
        "token_type": 'bearer'
    }

def sign_token(
    user_id: int,
    role: bool,
    exp:float = time.time()+3600) -> Dict[str, str]:
    # 3600 = 1 hr
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': exp
    }
    token = jwt.encode(payload, JWT_CONF['secret'], algorithm=JWT_CONF['algorithm'])
    return token_response(token)

def decode_token(token:str) -> dict:
    try:
        decoded = jwt.decode(token, JWT_CONF['secret'], algorithms=[JWT_CONF['algorithm']])
        return decoded
    except jwt.InvalidSignatureError:
        # Signature verification failed
        return {'verification_failed': 'signature'}
    except jwt.ExpiredSignatureError:
        # Signature has expired
        return {'verification_failed': 'expires'}
    except Exception as e:
        return {'unknown_error': e}
