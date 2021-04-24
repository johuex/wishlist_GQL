"""GQL Schema description"""
from graphene import relay, Union, Enum
from app.models import User as UserModel, FriendRequests as FriendRequestsModel, FriendShip as FriendShipModel,\
    Item as ItemModel, Group as GroupModel, Wishlist as WishlistModel,\
    ItemPicture as ItemPictureModel, GroupUser as GroupUserModel, GroupList as GroupListModel, \
    ItemGroup as ItemGroupModel
from app.auth import token_check
from app.database import db_session as db

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

    def resolve_items(self, info):
        pass


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

    def resolve_user_lists(parent, info):
        pass

    def resolve_friend_requests(parent, info):
        pass

    @token_check
    def resolve_items_owner(parent, info, id_from_token):
        item = db.query(Item).filter_by(owner_id=int(parent.id)).first()
        if item.access_level == 'ALL':
            return item
        if item.access_level == 'NOBODY' and item.owner_id == parent.id:
            return item
        if item.access_level == 'FRIENDS' and db.query(FriendShip).filter_by(user_id_1=item.owner.id,
                                                                       user_id_2 = parent.id).first():
            return item
        raise Exception("Access denied!")

    def resolve_items_giver(parent, info):
        pass


class ItemPicture(SQLAlchemyObjectType):
    class Meta:
        description = "Table for picture's path of items"
        model = ItemPictureModel
        interfaces = (relay.Node,)


class GroupUser(SQLAlchemyObjectType):
    class Meta:
        description = "Table for users and their roles in groups"
        model = GroupUserModel
        interfaces = (relay.Node,)


class GroupList(SQLAlchemyObjectType):
    class Meta:
        description = "Table for lists in groups"
        model = GroupListModel
        interfaces = (relay.Node,)


class ItemGroup(SQLAlchemyObjectType):
    class Meta:
        description = "Table for items in groups"
        model = ItemGroupModel
        interfaces = (relay.Node,)


class Search(Union):
    class Meta:
        description = "Union returning search of Wishlists, Items and Users"
        types = (Wishlist, Item, User)


class UsersWishlistsAndItems(Union):
    class Meta:
        description = "Union returning Wishlists and Items of User"
        types = (Wishlist, Item)

