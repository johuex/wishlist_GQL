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


