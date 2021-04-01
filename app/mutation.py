from graphene import ObjectType, Mutation, String, Boolean, Field, ID, InputObjectType
from .schema import User
from .database import db_session as db


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

    def mutate(root, info, user_data):
        if db.query(User).filter_by():
            # ошибка повторения
            pass
        if db.query(User).filter_by():
            # ошибка повторения
            pass
        db.add(User(email=user_data.email, password=user_data.password, user_name=user_data.user_name))
        db.commit()
        return RegisterUser(ok=True, id=db.query(User.id).filter_by(email=user_data.email))


class Mutation(ObjectType):
    register = RegisterUser.Field()
