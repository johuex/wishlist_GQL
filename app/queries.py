from graphene import ObjectType, relay, List, Field, ID, String
from app.schema import User as UserQl, Wishlist as WishlistQl, Item as ItemQl, Group as GroupQl
from graphene_sqlalchemy import SQLAlchemyConnectionField


class Query(ObjectType):
    node = relay.Node.Field()
    user = SQLAlchemyConnectionField(UserQl.connection, user_id=ID(), nickname=String(), token=String(required=True),
                                     refresh_token=String())
    wishlist = SQLAlchemyConnectionField(WishlistQl.connection, list_id=ID())
    item = SQLAlchemyConnectionField(ItemQl.connection, item_id=ID())
    group = SQLAlchemyConnectionField(GroupQl.connection, group_id=ID())

    '''async def resolve_user(parent, info, user_id, token):
        """return user by id"""
        id_from_token = int(au.decode_token(token))
        if int(user_id) == id_from_token:
            return db.query(UserDB).filter_by(id=user_id).first()
        else:
            # TODO сделать грамотный вывод об ошибке в ???
            return error_response(401, 'Access denied')



    '''