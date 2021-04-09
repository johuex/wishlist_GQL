"""GQL Schema description"""
from graphene import relay, ObjectType, Union, List, NonNull
from app.models import User as UserModel, FriendRequests as FriendRequestsModel, FriendShip as FriendShipModel,\
    Item as ItemModel, Group as GroupModel, Wishlist as WishlistModel,\
    RoleEnum as RoleEumModel, DegreeEnum as DegreeEnumModel, AccessLevelEnum as AccessLevelEnumModel, \
    StatusEnum as StatusEnumModel

from graphene_sqlalchemy import SQLAlchemyObjectType


class FriendRequests(SQLAlchemyObjectType):
    class Meta:
        description = "Table of requests for friendship"
        model = FriendRequestsModel
        '''
    user_id_from = User()
    user_id_to = User() '''


class FriendShip(SQLAlchemyObjectType):
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


class Wishlist(SQLAlchemyObjectType):
    class Meta:
        description = "Table of Wishlists"
        model = WishlistModel


class Group(SQLAlchemyObjectType):
    class Meta:
        description = "Table for GroupLists"
        model = GroupModel


class User(SQLAlchemyObjectType):
    class Meta:
        description = 'Table of Users'
        model = UserModel
        # as tuple: () = (smthg,)
        interfaces = (relay.Node,)  # interfaces where Users used
        # possible_types = ()  # types used in Users
        exclude = ("password_hash", "friends_from", "friends_1")
    #users_items = List(Item)
    #users_wishlists = List(Wishlist)


class RoleEnum(ObjectType):
    class Meta:
        description = "Enum for roles on grouplists"
        model = RoleEumModel


class DegreeEnum(ObjectType):
    class Meta:
        description = "Enum for degree in items"
        model = DegreeEnumModel


class AccessLevelEnum(ObjectType):
    class Meta:
        description = "Enum for access_levels"
        model = AccessLevelEnumModel


class StatusEnum(ObjectType):
    class Meta:
        description = "Enum for status of items"
        model = StatusEnumModel


class UsersWishlistsAndItems(Union):
    class Meta:
        description = "Union returning Wishlists and Items of User"
        types = (Wishlist, Item)


class Search(Union):
    class Meta:
        description = "Union returning search of Wishlists, Items and Users"
        types = (Wishlist, Item, User)