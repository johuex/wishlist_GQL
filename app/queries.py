from graphene import ObjectType, relay, List, Field, ID, String
from graphene_sqlalchemy import SQLAlchemyConnectionField
from .schema import User, Wishlist, Item, Friendship
from .database import db_session as db


class Query(ObjectType):
    node = relay.Node.Field()
    # users GET-queries
    users = List(User)
    user_by_id = Field(User, user_id=ID(required=True))
    user_by_nickname = Field(User, nickname=String(required=True))
    friends = List(User, user_id=ID(required=True))
    user_items = List(Item)
    user_wishlists = List(Wishlist)

    # wish_items GET-queries
    wish_items = List(Item)

    # wishlists GET-queries
    wishlists = List(Wishlist)
    items_in_wishlists = List(Item)

    async def resolve_user_by_id(parent, info, user_id):
        """return user by id"""
        return db.query(User).filter_by(id=user_id).first()

    async def resolve_user_by_nickname(parent, info, nickname):
        """return user by nickname"""
        return db.query(User).filter_by(nickname=nickname).first()

    async def resolve_users(parent, info):
        """return all users"""
        return db.query(User).all()

    async def resolve_friends(parent, info, user_id):
        """return all friends of user"""
        return db.query(User).filter_by(id=db.query(Friendship).filter_by(user_id_1=user_id)).all()


    async def resolve_wish_items(parent, info):
        """return all wish_items"""
        return db.query(Item).all()

    async def resolve_wishlists(parent, info):
        """return all wishlists"""
        return db.query(Item).all()
