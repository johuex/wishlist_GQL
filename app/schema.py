"""GQL Schema description"""
from graphene import relay, ObjectType, Union, List, Field
from app.models import User as UserModel, FriendRequests as FriendRequestsModel, FriendShip as FriendShipModel,\
    Item as ItemModel, Group as GroupModel, Wishlist as WishlistModel,\
    RoleEnum as RoleEumModel, DegreeEnum as DegreeEnumModel, AccessLevelEnum as AccessLevelEnumModel, \
    StatusEnum as StatusEnumModel

from graphene_sqlalchemy import SQLAlchemyObjectType


class FriendRequests(SQLAlchemyObjectType):
    class Meta:
        description = "Table of requests for friendship"
        model = FriendRequestsModel
        interfaces = (relay.Node,)


class FriendShip(SQLAlchemyObjectType):
    class Meta:
        description = "Table for friendship"
        model = FriendShipModel
        interfaces = (relay.Node,)


class Item(SQLAlchemyObjectType):
    class Meta:
        description = "Table for items"
        model = ItemModel
        interfaces = (relay.Node,)


class Wishlist(SQLAlchemyObjectType):
    class Meta:
        description = "Table of Wishlists"
        model = WishlistModel
        interfaces = (relay.Node,)



class Group(SQLAlchemyObjectType):
    class Meta:
        description = "Table for GroupLists"
        model = GroupModel
        interfaces = (relay.Node,)


class User(SQLAlchemyObjectType):
    class Meta:
        description = 'Table of Users'
        model = UserModel
        # as tuple: () = (smthg,)
        interfaces = (relay.Node,)  # interfaces where Users used
        # possible_types = ()  # types used in Users
        exclude_fields = ('password_hash', 'token', 'refresh_token', 'users_lists')




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
