from graphene import ObjectType, relay, List, Field, ID, String
from fastapi import HTTPException
from .models import User as UserDB, Wishlist as WishlistDB, Item as ItemDB, FriendShip as FriendShipDB
from .schema import User as UserQl, Wishlist as WishlistQl, Item as ItemQl, FriendShip as FriendShipQl

from .database import db_session as db
from .auth import au


class Query(ObjectType):
    node = relay.Node.Field()
    # users GET-queries
    users = List(UserQl)
    user_by_id = Field(UserQl, user_id=ID(required=True), token=String(required=True))
    user_by_nickname = Field(UserQl, nickname=String(required=True))
    friends = List(UserQl, user_id=ID(required=True))
    user_items = List(ItemQl)
    user_wishlists = List(WishlistQl)

    # wish_items GET-queries
    wish_items = List(ItemQl)

    # wishlists GET-queries
    wishlists = List(WishlistQl)
    items_in_wishlists = List(ItemQl)

    async def resolve_user_by_id(parent, info, user_id, token):
        """return user by id"""
        user_id = au.decode_token(str(token))
        if user_id["sub"] == db.query(UserDB.id).filter_by(token=token).first():
            return db.query(UserDB).filter_by(id=user_id).first()
        else:
            raise HTTPException(status_code=401, detail='Access denied')


    async def resolve_user_by_nickname(parent, info, nickname):
        """return user by nickname"""
        return db.query(UserDB).filter_by(nickname=nickname).first()

    async def resolve_users(parent, info):
        """return all users"""
        return db.query(UserDB).all()

    async def resolve_friends(parent, info, user_id):
        """return all friends of user"""
        return db.query(UserDB).filter_by(id=db.query(FriendShipDB).filter_by(user_id_1=user_id)).all()


    async def resolve_wish_items(parent, info):
        """return all wish_items"""
        return db.query(ItemDB).all()

    async def resolve_wishlists(parent, info):
        """return all wishlists"""
        return db.query(ItemDB).all()
