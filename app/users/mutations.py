from graphene import ObjectType, Mutation, String, Boolean, Field, ID, InputObjectType
from graphql import GraphQLError
from sqlalchemy import update

from app.models import User
from app.database import db_session as db
from app.auth import au


class UserInput(InputObjectType):
    email = String(required=True)
    password = String(required=True)
    user_name = String(required=True)  #  имя пользователя
    nickname = String(required=True)


class RegisterUser(Mutation):
    class Arguments:
        user_data = UserInput(required=True)

    ok = Boolean()
    id = ID()
    message = String()

    def mutate(root, info, user_data):
        if db.query(User).filter_by(email=user_data.email).first():
            #raise GraphQLError("An account is already registered for this mailbox")
            return RegisterUser(ok=False, message="An account is already registered for this mailbox")
        if db.query(User).filter_by(nickname=user_data.nickname).first():
            return RegisterUser(ok=False, message="An account is already registered for this nickname")

        user_id = db.add(User(email=user_data.email, password_hash=au.get_password_hash(user_data.password),
                         user_name=user_data.user_name)).returning(User.id)
        db.commit()
        return RegisterUser(ok=True, message="Registration done!", id=user_id)


class LoginUser(Mutation):
    class Arguments:
        email = String(required=True)
        password = String(required=True)

    token = String()
    ok = Boolean()
    message = String()

    def mutate(self, info, email, password):
        user = db.query(User).filter_by(email=email).first()
        if au.verify_password(password, user.password_hash):
            token = au.encode_token(user.id)
            user.token = token
            db.commit()
            return LoginUser(ok=True, message="Token issued", token=token)
        else:
            return LoginUser(ok=False, message="Invalid password or email")


class UserMutation(ObjectType):
    register = RegisterUser.Field()
    authorization = LoginUser.Field()
