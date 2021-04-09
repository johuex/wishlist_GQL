from graphene import ObjectType, relay, List, Field, ID, String
from app.models import User as UserDB, Wishlist as WishlistDB, Item as ItemDB, FriendShip as FriendShipDB
from app.schema import User as UserQl, Wishlist as WishlistQl, Item as ItemQl, FriendShip as FriendShipQl
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField

from app.database import db_session as db
from app.auth import au
from app.errors import *


class UserQuery(ObjectType):
    node = relay.Node.Field()

    user = SQLAlchemyConnectionField(UserQl.connection, user_id=ID(), nickname=String(), token=String(required=True))
    #user = Field(UserQl, user_id=ID(), nickname=String(), token=String(required=True))




    async def resolve_user(parent, info, user_id, token):
        """return user by id"""
        id_from_token = int(au.decode_token(token))
        if int(user_id) == id_from_token:
            return db.query(UserDB).filter_by(id=user_id).first()
        else:
            # TODO сделать грамотный вывод об ошибке в ???
            return error_response(401, 'Access denied')



