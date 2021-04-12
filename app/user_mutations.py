from graphene import ObjectType, Mutation, String, Boolean, Field, ID, InputObjectType


from app.models import User
from app.database import db_session as db
from app.auth import au


class UserInputRegistration(InputObjectType):
    """Input for classic registration"""
    email = String(required=True)
    password = String(required=True)
    user_name = String(required=True)  #  имя пользователя
    nickname = String(required=True)


class FastUserInputRegistration(InputObjectType):
    """Input for fast registration"""
    email = String(required=True)
    user_name = String(required=True)  # имя пользователя


class ClassicRegisterUser(Mutation):
    """Classic registration"""
    class Arguments:
        user_data = UserInputRegistration(required=True)

    ok = Boolean()
    message = String()

    def mutate(root, info, user_data):
        if db.query(User).filter_by(email=user_data.email).first():
            #raise GraphQLError("An account is already registered for this mailbox")
            return ClassicRegisterUser(ok=False, message="An account is already registered for this mailbox")
        if db.query(User).filter_by(nickname=user_data.nickname).first():
            return ClassicRegisterUser(ok=False, message="An account is already registered for this nickname")

        db.add(User(email=user_data.email, password_hash=au.get_password_hash(user_data.password),
                         user_name=user_data.user_name))
        db.commit()
        return ClassicRegisterUser(ok=True, message="Registration done!")


class FastRegisterUser(Mutation):
    """Fast registration for those who don't want to registrate, but want to reserve item"""
    class Arguments:
        user_data = FastUserInputRegistration(required=True)

    ok = Boolean()
    message = String()

    def mutate(root, info, user_data):
        if db.query(User).filter_by(email=user_data.email).first():
            #raise GraphQLError("An account is already registered for this mailbox")
            return ClassicRegisterUser(ok=False, message="An account is already registered for this mailbox")
        db.add(User(email=user_data.email, user_name=user_data.user_name))
        db.commit()
        return ClassicRegisterUser(ok=True, message="Registration done!")


class LoginUser(Mutation):
    """Authorization and returning token and refresh_token"""
    class Arguments:
        email = String(required=True)
        password = String(required=True)

    token = String()
    refresh_token = String()
    ok = Boolean()
    message = String()

    def mutate(self, info, email, password):
        user = db.query(User).filter_by(email=email).first()
        if au.verify_password(password, user.password_hash):
            token = au.encode_token(user.id)
            # refresh_token = au.encode_token(user.id, True)
            user.token = token
            # user.refresh_token = refresh_token
            db.commit()
            return LoginUser(ok=True, message="Token issued", token=token)
        else:
            return LoginUser(ok=False, message="Invalid password or email")


class UserMutation(ObjectType):
    classic_register = ClassicRegisterUser.Field()
    fast_register = FastRegisterUser.Field()
    authorization = LoginUser.Field()
