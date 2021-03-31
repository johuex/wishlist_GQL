"""GQL Schema description"""
from graphene import relay, ObjectType, ID, String, NonNull, List, Enum, Date, DateTime, Int
from app.models import User as UserModel, FriendRequests as FriendRequestsModel, FriendShip as FriendShipModel,\
    Item as ItemModel, Group as GroupModel, Wishlist as WishlistModel
from graphene_sqlalchemy import SQLAlchemyObjectType


class FriendRequests(SQLAlchemyObjectType):
    class Meta:
        description = "Table of requests for friendship"
        model = FriendRequestsModel
        '''
    user_id_from = User()
    user_id_to = User() '''


class Friendship(SQLAlchemyObjectType):
    class Meta:
        description = "Table for friendship"
        model = FriendShipModel
    '''user_id_1 = User()
    user_id_2 = User()'''


class Item(SQLAlchemyObjectType):
    class Meta:
        description = "Table for items"
        model = ItemModel
    '''item_id = NonNull(ID(name='id'))
    title = NonNull(String())
    about = String()
    access_level = NonNull(AccessLevel())
    status = NonNull(Status())
    giver_id = User()
    date_creation = NonNull(DateTime())
    date_for_status = DateTime()  # changing status date
    degree = NonNull(Degree())
    path_to_picture = List(String())'''


class User(SQLAlchemyObjectType):
    class Meta:
        description = 'Table of Users'
        model = UserModel
        # as tuple: () = (smthg,)
        interfaces = (relay.Node)  # interfaces where Users used
        possible_types = ()  # types used in Users


class Wishlist(SQLAlchemyObjectType):
    class Meta:
        description = "Table of Wishlists"
        model = WishlistModel



class Group(SQLAlchemyObjectType):
    class Meta:
        description = "Table for GroupLists"
        model = GroupModel
