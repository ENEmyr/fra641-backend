from fastapi import HTTPException, Request
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer

from helpers.auth_handler import decode_token


class JWTBearer(HTTPBearer):
    def __init__(
            self,
            auto_error:bool = True,
            verify_admin:bool = False):
        super(JWTBearer, self).__init__(auto_error=auto_error)
        self.verify_admin = verify_admin
    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request=request)
        if credentials:
            if not credentials.scheme == 'Bearer':
                raise HTTPException(status_code=401, detail='Invalid authentication scheme.')
            is_admin = self.verify_jwt(credentials.credentials)
            if self.verify_admin:
                if not is_admin:
                    raise HTTPException(status_code=403, detail='Not enough privileges.')
            return credentials.credentials
        else:
            raise HTTPException(status_code=401, detail='Invalid authorization code.')
    def verify_jwt(self, token: str) -> int:
        # return role that was collected in payload if passed verification.
        isTokenValid: int = -1
        payload = decode_token(token)
        if 'verification_failed' not in payload.keys() or 'unknown_error' not in payload.keys():
            isTokenValid = payload['role'] 
        if isTokenValid == -1:
            raise HTTPException(status_code=401, detail='Invalid token or expired token.')
        return isTokenValid
