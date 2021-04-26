from graphene import ObjectType, Mutation, String, Boolean, Date, ID, InputObjectType
from graphene_file_upload.scalars import Upload
from app.models import User, FriendShip as FS, FriendRequests as FR
from app.database import db_session as db
from app.auth import au, token_required, last_seen_set, token_check
from app.config import Config
from app.s3 import *


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
    #userpic = ???
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
    """Returning new access_token by refresh_token"""
    class Arguments:
        user_id = ID(required=True)
        # TODO передавать его в Autorization ???
        refresh_token = String(required=True)

    ok = Boolean()
    access_token = String()
    message = String()

    @token_check
    def mutate(self, info, user_id, refresh_token, id_from_token):
        if int(user_id) != id_from_token:
            return RefreshToken(ok=False, message="Refresh token missed!", access_token="")
        else:
            new_access_token, revoked_refresh_token = au.refresh_token(refresh_token)
            user = db.query(User).filter_by(id=id_from_token).first()
            user.refresh_token = revoked_refresh_token
            db.commit()
            return RefreshToken(ok=True, message="New access_token generated!", access_token=new_access_token)


class ChangePassword(Mutation):
    class Arguments:
        old_password = String(required=True)
        new_password = String(required=True)

    ok = String()
    message = String()

    @token_check
    def mutate(self, info, old_password, new_password, id_from_token):
        user = db.query(User).filter_by(id=id_from_token).first()
        if old_password == au.verify_password(user.password_hash):
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
            name = 'user_' + str(user.id)
            url = f"https://" + Config.bucket + "s3.amazonaws.com" + name
            upload_file(user_pic, Config.bucket, name)
            user.userpic = name
            db.commit()
            return UploadUserPicture(ok=True, message="Userpic have been uploaded")
        else:
            return UploadUserPicture(ok=False, message="Userpic haven't been upload")


class UserMutation(ObjectType):
    classic_register = ClassicRegisterUser.Field()
    fast_register = FastRegisterUser.Field()
    authorization = LoginUser.Field()
    refresh_access_token = RefreshToken.Field()
    edit_user = EditUser.Field()
    change_password = ChangePassword.Field()
    send_friend_request = SendFriendRequest.Field()
    accept_friend_request = AcceptFriendRequest.Field()
    reject_friend_request = RejectFriendRequest.Field()
    cancel_friend_request = CancelFriendRequest.Field()
    remove_from_friends = RemoveFromFriends.Field()
    upload_userpic = UploadUserPicture.Field()

