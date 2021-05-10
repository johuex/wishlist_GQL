import jwt
from fastapi import HTTPException
from passlib.context import CryptContext
from datetime import datetime, timedelta
from app.config import Config
from app.database import db_session as db
import functools
from app.models import User


class AuthHandler:
    """token authentication and authorization class"""
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    secret = Config.SECRET_KEY

    def get_password_hash(self, password):
        """password -> password_hash"""
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_password):
        """check password by password_hash"""
        return self.pwd_context.verify(plain_password, hashed_password)

    def encode_token(self, user_id, experation=15):
        """creating token"""
        payload = {
            'exp': datetime.utcnow() + timedelta(days=0, minutes=experation),
            'iat': datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(
            payload,
            self.secret,
            algorithm='HS256')

    def decode_token_without_checking(self, token):
        try:
            payload = jwt.decode(token, self.secret, algorithms=['HS256'])
            return payload['sub']
        except jwt.InvalidTokenError:
            raise Exception('Invalid token!')
            #raise HTTPException(status_code=401, detail='Invalid token')

    def decode_token_with_checking(self, token):
        try:
            payload = jwt.decode(token, self.secret, algorithms=['HS256'])
            return payload['sub']
        except jwt.ExpiredSignatureError:
            raise Exception('Signature has expired. Authorize again or refresh access_token!')
            #raise HTTPException(status_code=401, detail='Signature has expired. Authorize again or refresh access_token!')
        except jwt.InvalidTokenError:
            raise Exception('Invalid token')
            #raise HTTPException(status_code=401, detail='Invalid token')

    def revoke_token(self, user_id):
        payload = {
            'exp': datetime.utcnow() + timedelta(days=1, minutes=0),
            'iat': datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(
            payload,
            self.secret,
            algorithm='HS256')


au = AuthHandler()


def token_required(func):
    """Returning User_ID from token, where token is required"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        token = args[1].context['request'].headers.raw[5][1][4:].decode("utf-8")
        if token is None:
            raise Exception("Token missed!")
        else:
            id_from_token = au.decode_token_with_checking(token)
            return func(*args, **kwargs, id_from_token=id_from_token)
    return wrapper


def token_check(func):
    """Returning User_ID from token, where token is default in params"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        id_from_token = 0
        token = args[1].context['request'].headers.raw[5][1][4:].decode("utf-8")
        if token is not None:
            id_from_token = au.decode_token_with_checking(token)
        return func(*args, **kwargs, id_from_token=id_from_token)
    return wrapper


def last_seen_set(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if kwargs.get("id_from_token") is not None and kwargs["id_from_token"] is not None:
            if kwargs["id_from_token"] != 0:
                user = db.query(User).filter_by(id=kwargs["id_from_token"]).first()
                user.last_seen = datetime.utcnow()
                db.commit()

        return func(*args, **kwargs)

    return wrapper
