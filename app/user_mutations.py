import random

from graphene import ObjectType, Mutation, String, Boolean, Date, ID, InputObjectType
from graphene_file_upload.scalars import Upload
from app.models import User, FriendShip as FS, FriendRequests as FR
from app.database import db_session as db
from app.auth import au, token_required, last_seen_set, token_check
from app.config import Config
from app.s3 import *
from app.email_server import e_host


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
    phone_number = String()
    user_name = String()
    surname = String()
    about = String()
    birthday = Date()
    nickname = String()
    email = String()


class ClassicRegisterUser(Mutation):
    """Classic registration"""
    class Arguments:
        user_data = UserInputRegistration(required=True)

    ok = Boolean()
    message = String()
    ID = ID()

    def mutate(root, info, user_data):
        if db.query(User).filter_by(email=user_data.email).first():
            return ClassicRegisterUser(ok=False, message="An account is already registered for this mailbox")
        if db.query(User).filter_by(nickname=user_data.nickname).first():
            return ClassicRegisterUser(ok=False, message="An account is already registered for this nickname")
        new_user = User(email=user_data.email, password_hash=au.get_password_hash(user_data.password),
                         user_name=user_data.user_name, nickname=user_data.nickname, userpic="users/user_0.png")
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return ClassicRegisterUser(ok=True, message="Registration done!", ID=new_user.id)


class FastRegisterUser(Mutation):
    """Fast registration for those who don't want to registrate, but want to reserve item"""
    class Arguments:
        user_data = FastUserInputRegistration(required=True)

    ok = Boolean()
    message = String()
    ID = ID()

    def mutate(root, info, user_data):
        if db.query(User).filter_by(email=user_data.email).first():
            return ClassicRegisterUser(ok=False, message="An account is already registered for this mailbox")
        code = random.randint(100000, 999999)
        e_host.send_email(user_data.email, "Confirm actions", user_data.user_name, "other/fast_registration.txt", code)
        new_user = User(email=user_data.email, user_name=user_data.user_name, password_hash=au.get_password_hash(code))
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return ClassicRegisterUser(ok=True, message="Registration done!", ID=new_user.id)


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
            refresh_token = au.encode_token(user.id, experation=1440)  # 1440 min = 1 day
            user.token = token
            user.refresh_token = refresh_token
            db.commit()
            return LoginUser(ok=True, message="Token issued", token=token, refresh_token=refresh_token)
        else:
            return LoginUser(ok=False, message="Invalid password or email")


class EditUser(Mutation):
    """Editing user info"""
    class Arguments:
        data = UserEditInput(required=True)

    ok = Boolean()
    message = String()

    @token_required
    @last_seen_set
    def mutate(self, info, data, id_from_token):
        user = db.query(User).filter_by(id=id_from_token).first()
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


class RefreshToken(Mutation):
    """Returning new access_token and refresh_token"""
    class Arguments:
        token = String(required=True)
        refresh_token = String(required=True)

    ok = Boolean()
    access_token = String()
    refresh_token = String()
    message = String()

    def mutate(self, info, token, refresh_token):
        user = db.query(User).filter(token==token and refresh_token==refresh_token).first()
        if user is None:
            return RefreshToken(ok=False, message="ERROR!")
        user.token = au.encode_token(user.id)
        user.refresh_token = au.encode_token(user.id, experation=1440)
        db.commit()
        return RefreshToken(ok=False, message="ERROR!", access_token=user.token, refresh_token=user.refresh_token)


class ChangePassword(Mutation):
    class Arguments:
        email = String()
        old_password = String(required=True)
        new_password = String(required=True)

    ok = String()
    message = String()

    @token_check
    def mutate(self, info, old_password, new_password, email):
        user = db.query(User).filter_by(email=email).first()
        if user is None:
            return ChangePassword(ok=False, message="User with this email is None!")
        if au.verify_password(old_password, user.password_hash) is False:
            return ChangePassword(ok=False, message="Old password is incorrect!")
        user.password_hash = au.get_password_hash(new_password)
        return ChangePassword(ok=True, message="Password was changed!")


class SendFriendRequest(Mutation):
    """Send request for friendhsip"""
    class Arguments:
        to_user_id = ID(required=True)

    ok = Boolean()
    message = String()

    @token_check
    def mutate(self, info, to_user_id, id_from_token):
        if db.query(FS).filter_by(user_id_1=id_from_token, user_id_2=to_user_id).first() is not None:
            SendFriendRequest(ok=False, message="You are already friends!")
        if db.query(FR).filter_by(user_id_from=id_from_token, user_id_to=to_user_id).first() is not None:
            SendFriendRequest(ok=False, message="You have already sent friend request to this user!")
        db.add(FR(user_id_from=id_from_token, user_id_to=to_user_id))
        db.commit()
        return SendFriendRequest(ok=True, message="Friend request has been sent!")


class AcceptFriendRequest(Mutation):
    class Arguments:
        from_user_id = ID(required=True)

    ok = Boolean()
    message = String()

    @token_check
    def mutate(self, info, from_user_id, id_from_token):
        fr = db.query(FR).filter_by(user_id_from=from_user_id, user_id_to=id_from_token).first()
        if (fr is not None) and \
                (db.query(FS).filter_by(user_id_1=id_from_token, user_id_2=from_user_id).first() is None):
            db.add(FS(user_id_1=from_user_id, user_id_2=id_from_token))
            db.add(FS(user_id_2=from_user_id, user_id_1=id_from_token))
            db.delete(fr)
            db.commit()
            return AcceptFriendRequest(ok=True, message="Friend request has been accepted!")
        else:
            return AcceptFriendRequest(ok=False, message="Friend request hasn't been accepted!")


class RejectFriendRequest(Mutation):
    class Arguments:
        from_user_id = ID(required=True)

    ok = Boolean()
    message = String()

    @token_check
    def mutate(self, info, from_user_id, id_from_token):
        fr = db.query(FR).filter_by(user_id_from=from_user_id, user_id_to=id_from_token).first()
        if fr is not None:
            db.delete(fr)
            db.commit()
            return RejectFriendRequest(ok=True, message="Friend request has been rejected!")
        else:
            return RejectFriendRequest(ok=False, message="Friend request hasn't been rejected!")


class CancelFriendRequest(Mutation):
    class Arguments:
        to_user_id = ID(required=True)
        from_user_id = ID(required=True)

    ok = Boolean()
    message = String()

    @token_check
    def mutate(self, info, to_user_id, from_user_id, id_from_token):
        if id_from_token != int(from_user_id):
            return CancelFriendRequest(ok=False, message="Access denied!")
        fr = db.query(FR).filter_by(user_id_from=id_from_token, user_id_to=to_user_id).first()
        if fr is not None:
            db.delete(fr)
            db.commit()
            return CancelFriendRequest(ok=True, message="Friend request has been canceled!")
        else:
            return CancelFriendRequest(ok=True, message="Friend request hasn't been canceled!")


class RemoveFromFriends(Mutation):
    class Arguments:
        friend_id = String(required=True)

    ok = Boolean()
    message = String()

    @token_check
    def mutate(self, info, friend_id, id_from_token):
        fr1 = db.query(FS).filter_by(user_id_1=id_from_token, user_id_2=friend_id).first()
        fr2 = db.query(FS).filter_by(user_id_2=id_from_token, user_id_1=friend_id).first()
        if fr1 is not None and fr2 is not None:
            db.delete(fr1)
            db.delete(fr2)
            db.commit()
            return RemoveFromFriends(ok=True, message="Friend has been removed :-(")
        else:
            return RemoveFromFriends(ok=True, message="Friend hasn't been removed :-)")


class UploadUserPicture(Mutation):
    class Arguments:
        user_pic = Upload(required=True)

    ok = Boolean()
    message = String()

    @token_required
    def mutate(self, info, user_pic, id_from_token):
        if check_format(user_pic):
            user = db.query(User).filter_by(id=id_from_token).first()
            name = 'users/user_' + str(user.id)
            if upload_file(user_pic, Config.bucket, name):
                user.userpic = name
                db.commit()
                return UploadUserPicture(ok=True, message="Userpic have been uploaded")
        return UploadUserPicture(ok=False, message="Userpic haven't been upload")


class ResetPassword(Mutation):
    class Arguments:
        email = String(required=True)

    ok = Boolean()
    message = String()

    def mutate(self, info, email):
        user = db.query(User).filter_by(email=email).first()
        if user is None:
            raise Exception("No user with this email!")
        code = random.randint(100000, 999999)
        e_host.send_email(user.email, "Reset Password", user.user_name, "other/reset_password.txt", code)
        user.password_hash = au.get_password_hash(str(code))
        db.commit()
        return ResetPassword(ok=True, message="Confirm email send to your email!")


class UserMutation(ObjectType):
    classic_register = ClassicRegisterUser.Field()
    # fast_register = FastRegisterUser.Field()
    authorization = LoginUser.Field()
    refresh_tokens = RefreshToken.Field()
    edit_user = EditUser.Field()
    change_password = ChangePassword.Field()
    reset_password = ResetPassword.Field()
    send_friend_request = SendFriendRequest.Field()
    accept_friend_request = AcceptFriendRequest.Field()
    reject_friend_request = RejectFriendRequest.Field()
    cancel_friend_request = CancelFriendRequest.Field()
    remove_from_friends = RemoveFromFriends.Field()
    upload_userpic = UploadUserPicture.Field()


