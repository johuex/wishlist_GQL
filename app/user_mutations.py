from graphene import ObjectType, Mutation, String, Boolean, Date, ID, InputObjectType


from app.models import User
from app.database import db_session as db
from app.auth import au, token_required


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


class UserEditInput(InputObjectType):
    """Input for edit user"""
    user_id = ID()
    phone_number = String()
    user_name = String()
    surname = String()
    #userpic = ???
    about = String()
    birthday = Date()
    nickname = String()
    email = String()
    token = String()


class ClassicRegisterUser(Mutation):
    """Classic registration"""
    class Arguments:
        user_data = UserInputRegistration(required=True)

    ok = Boolean()
    message = String()

    def mutate(root, info, user_data):
        if db.query(User).filter_by(email=user_data.email).first():
            return ClassicRegisterUser(ok=False, message="An account is already registered for this mailbox")
        if db.query(User).filter_by(nickname=user_data.nickname).first():
            return ClassicRegisterUser(ok=False, message="An account is already registered for this nickname")

        db.add(User(email=user_data.email, password_hash=au.get_password_hash(user_data.password),
                         user_name=user_data.user_name, nickname=user_data.nickname))
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


class EditUser(Mutation):
    """Editing user info"""
    class Arguments:
        data = UserEditInput(required=True)

    ok = Boolean()
    message = String()

    @token_required
    def mutate(self, info, data, id_from_token):
        #id_from_token = int(au.decode_token(data.token))
        if int(data.user_id) != id_from_token:
            return EditUser(ok=False, message="Access denied!")
        user = db.query(User).filter_by(id=data.user_id).first()
        # check for '' and info duplication in account
        if data.user_name is not None and data.user_name != user.user_name:
            user.user_name = data.user_name
        if data.surname is not None and data.surname != user.surname:
            user.surname = data.surname
        if data.about is not None and data.about != user.about:
            user.about = data.about
        if data.birthday is not None and data.birthday != user.birthday:
            user.birthday = data.birthday
        if data.nickname is not None and data.nickname != user.nickname and not\
                db.query(User).filter_by(nickname=data.nickname).first():
            user.nickname = data.nickname
        if data.email is not None and data.email != user.email and not\
                db.query(User).filter_by(email=data.email).first():
            user.email = data.email
        if data.phone_number is not None and data.phone_number != user.phone_number:
            user.phone_number = data.phone_number
        if data.phone_number is not None and data.phone_number != user.phone_number:
            user.phone_number = data.phone_number

        db.commit()
        return EditUser(ok=True, message="User edited!")


class UserMutation(ObjectType):
    classic_register = ClassicRegisterUser.Field()
    fast_register = FastRegisterUser.Field()
    authorization = LoginUser.Field()
    edit_user = EditUser.Field()
