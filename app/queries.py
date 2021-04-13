from graphene import ObjectType, relay, Field, ID, String
from app.schema import User as UserQl, Wishlist as WishlistQl, Item as ItemQl, Group as GroupQl
from graphene_sqlalchemy import SQLAlchemyConnectionField
from app.models import User as UserDB, Wishlist as WishlistDB, Item as ItemDB, Group as GroupDB,\
    FriendShip as FSDB
from app.database import db_session as db
from app.errors import *
from app.auth import au


class Query(ObjectType):
    node = relay.Node.Field()
    user = Field(UserQl, user_id=ID(required=True))
    wishlist = Field(WishlistQl, list_id=ID(required=True), token=String())
    item = Field(ItemQl, item_id=ID(required=True), token=String())
    group = Field(GroupQl, group_id=ID(required=True), token=String())


    #all_users = SQLAlchemyConnectionField(UserQl.connection)
    #all_wishlists = SQLAlchemyConnectionField(WishlistQl.connection)
    #all_items = SQLAlchemyConnectionField(ItemQl.connection)
    #all_groups = SQLAlchemyConnectionField(GroupQl.connection)
    # it's an example for working with token
    '''async def resolve_user(parent, info, user_id, token):
        """return user by id"""
        id_from_token = int(au.decode_token(token))
        if int(user_id) == id_from_token:
            return db.query(UserDB).filter_by(id=user_id).first()
        else:
            # TODO сделать грамотный вывод об ошибке в ???
            return error_response(401, 'Access denied')
    '''
    async def resolve_user(parent, info, user_id):
        return db.query(UserDB).filter_by(id=int(user_id)).first()

    async def resolve_wishlist(parent, info, list_id, token):
        id_from_token = int(au.decode_token(token))
        wishlist = db.query(WishlistDB).filter_by(id=list_id).first()
        if (wishlist.user_id == id_from_token) or \
            (wishlist.access_level == 'FRIENDS' and db.query(FSDB).filter_by(user_id_1=wishlist.user_id,
                                                                             user_id_2=id_from_token).first()):
            # if it's owner of wishlist or his friend - show it
            return wishlist
        else:
            # access denied for all except owner
            raise Exception('Access denied!')

    async def resolve_item(parent, info, item_id, token):
        id_from_token = int(au.decode_token(token))
        item = db.query(ItemDB).filter_by(id=int(item_id)).first()
        if item.owner_id == id_from_token:
            return item
        elif item.access_level == 'FRIENDS' and db.query(FSDB).filter_by(user_id_1=item.user_id,
                                                                         user_id_2=id_from_token).first():
            return item
        elif item.giver_id == id_from_token:
            return item
        else:
            # access denied for all except owner
            raise Exception('Access denied!')

    async def resolve_group(parent, info, group_id, token):
        pass
