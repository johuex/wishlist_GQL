import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from app.config import Config
from app.database import db_session as db


class AuthHandler:
    """token authentication and authorization class"""
    security = HTTPBearer()
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    secret = Config.SECRET_KEY

    def get_password_hash(self, password):
        """password -> password_hash"""
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_password):
        """check password by password_hash"""
        return self.pwd_context.verify(plain_password, hashed_password)

    def encode_token(self, user_id, refresh=False):
        """creating token or refresh_token"""
        if refresh:
            payload = {
                'exp': datetime.utcnow() + timedelta(days=1, minutes=0),
                'iat': datetime.utcnow(),
                'sub': user_id
            }
        else:
            payload = {
                'exp': datetime.utcnow() + timedelta(days=0, minutes=15),
                'iat': datetime.utcnow(),
                'sub': user_id
            }
        return jwt.encode(
            payload,
            self.secret,
            algorithm='HS256')

    def decode_token(self, token):
        try:
            payload = jwt.decode(token, self.secret, algorithms=['HS256'])
            return payload['sub']
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Signature has expired. Authorize again!')
            # return self.refresh_token(refresh_token)
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail='Invalid token')

    def revoke_token(self, token):
        pass

    def refresh_token(self, refresh_token):
        try:
            payload = jwt.decode(refresh_token, self.secret, algorithms=['HS256'])
            return self.encode_token(payload['sub']), self.encode_token(payload['sub'])
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Signature has expired. Authorize again!')
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail='Invalid refresh_token')

    '''def auth_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)):

        return self.decode_token(auth.credentials)'''


au = AuthHandler()
