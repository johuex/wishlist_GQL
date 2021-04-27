"""GQL Schema description"""
from graphene import relay, Union, Enum, Interface, String, ID
from app.models import User as UserModel, FriendRequests as FriendRequestsModel, FriendShip as FriendShipModel,\
    Item as ItemModel, Group as GroupModel, Wishlist as WishlistModel,\
    ItemPicture as ItemPictureModel, GroupUser as GroupUserModel, GroupList as GroupListModel, \
    ItemGroup as ItemGroupModel, AccessLevelEnum
from app.auth import token_check
from app.database import db_session as db
from graphene_sqlalchemy import SQLAlchemyObjectType
from app.s3 import *
from app.config import Config


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

    @token_check
    def resolve_pictures(parent, info, id_from_token):
        # TODO add downloading pictures from S3
        if parent.access_level == AccessLevelEnum.ALL:
            return
        if parent.access_level == AccessLevelEnum.NOBODY and parent.owner_id == id_from_token:
            return
        if parent.access_level == AccessLevelEnum.FRIENDS and db.query(FriendShipModel).filter_by(user_id_1=parent.owner_id,
                                                                       user_id_2=id_from_token).first():
            return
        raise Exception("Access denied!")

    @token_check
    def resolve_in_wishlist(parent, info, id_from_token):
        return db.query(WishlistModel).filter_by(id=parent.list_id).first()

    @token_check
    def resolve_giver(parent, info, id_from_token):
        return db.query(UserModel).filter_by(id=parent.giver_id).first()

    @token_check
    def resolve_owner(parent, info, id_from_token):
        return db.query(UserModel).filter_by(id=parent.owner_id).first()

    @token_check
    def resolve_in_groups(parent, info, id_from_token):
        return db.query(ItemGroupModel).filter_by(item_id=parent.id).all()


class Wishlist(SQLAlchemyObjectType):
    class Meta:
        description = "Table of Wishlists"
        model = WishlistModel
        interfaces = (relay.Node,)

    @token_check
    def resolve_items(parent, info, id_from_token):
        if parent.access_level == AccessLevelEnum.ALL:
            return db.query(ItemModel).filter_by(list_id=parent.id).all()
        if parent.access_level == AccessLevelEnum.NOBODY and parent.user_id == id_from_token:
            return db.query(ItemModel).filter_by(list_id=parent.id).all()
        if parent.access_level == AccessLevelEnum.FRIENDS and db.query(FriendShipModel).filter_by(user_id_1=parent.user_id,
                                                                             user_id_2=id_from_token).first():
            return db.query(ItemModel).filter_by(list_id=parent.id, access_level=AccessLevelEnum.FRIENDS).all()
        raise Exception("Access denied!")

    @token_check
    def resolve_in_groups(parent, info, id_from_token):
        return db.query(GroupListModel).filter_by(wishlist_id=parent.id).all()


class Group(SQLAlchemyObjectType):
    class Meta:
        description = "Table for GroupLists"
        model = GroupModel
        interfaces = (relay.Node,)

    @token_check
    def resolve_users(parent, info, id_from_token):
        pass

    @token_check
    def resolve_items(parent, info, id_from_token):
        pass

    @token_check
    def resolve_lists(parent, info, id_from_token):
        pass


class User(SQLAlchemyObjectType):
    class Meta:
        description = 'Table of Users'
        model = UserModel
        interfaces = (relay.Node,)  # interfaces where Users used
        exclude_fields = ('password_hash', 'token', 'refresh_token', 'users_lists')

    @token_check
    def resolve_user_lists(parent, info, id_from_token):
        response = list()
        wishlists = db.query(ItemModel).filter_by(user__id=parent.id).all()
        if len(wishlists) == 0:
            return wishlists
        for wlist in wishlists:
            if wlist.access_level == AccessLevelEnum.ALL:
                response.append(wlist)
            if wlist.access_level == AccessLevelEnum.NOBODY and wlist.owner_id == id_from_token:
                response.append(wlist)
            if wlist.access_level == AccessLevelEnum.FRIENDS and db.query(FriendShipModel).filter_by(
                    user_id_1=wlist.owner_id,
                    user_id_2=id_from_token).first():
                response.append(wlist)
        if len(response) > 0:
            return response
        raise Exception("Access denied!")

    @token_check
    def resolve_friend_requests(parent, info, id_from_token):
        return db.query(FriendRequestsModel).filter_by(user_id_to=id_from_token).all()

    @token_check
    def resolve_friends(parent, info, id_from_token):
        return db.query(FriendShipModel).filter_by(user_id_1=id_from_token).all()

    @token_check
    def resolve_items_owner(parent, info, id_from_token):
        response = list()
        items = db.query(ItemModel).filter_by(owner_id=parent.id, list_id=None).all()
        if len(items) == 0:
            return items
        for item in items:
            if item.access_level == AccessLevelEnum.ALL:
                response.append(item)
            if item.access_level == AccessLevelEnum.NOBODY and item.owner_id == id_from_token:
                response.append(item)
            if item.access_level == AccessLevelEnum.FRIENDS and db.query(FriendShipModel).filter_by(user_id_1=item.owner_id,
                                                                       user_id_2=id_from_token).first():
                response.append(item)
        if len(response) > 0:
            return response
        raise Exception("Access denied!")

    @token_check
    def resolve_items_giver(parent, info, id_from_token):
        item = db.query(ItemModel).filter_by(owner_id=id_from_token).first()
        if len(item) == 0:
            return item
        if item.giver_id == id_from_token:
            return item
        raise Exception("Access denied!")

    @token_check
    def resolve_userpic(parent, info, id_from_token):
        """return url to download picture"""
        path = db.query(UserModel).filter_by(id=id_from_token).first()
        return download_file(Config.bucket + "users", path)


    @token_check
    def resolve_groups(parent, info, id_from_token):
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

    @token_check
    def resolve_users(aprent, info, id_from_token):
        pass

    @token_check
    def resolve_group(aprent, info, id_from_token):
        pass


class GroupList(SQLAlchemyObjectType):
    class Meta:
        description = "Table for lists in groups"
        model = GroupListModel
        interfaces = (relay.Node,)

    @token_check
    def resolve_lists(aprent, info, id_from_token):
        pass

    @token_check
    def resolve_group(aprent, info, id_from_token):
        pass


class ItemGroup(SQLAlchemyObjectType):
    class Meta:
        description = "Table for items in groups"
        model = ItemGroupModel
        interfaces = (relay.Node,)

    @token_check
    def resolve_item(aprent, info, id_from_token):
        pass

    @token_check
    def resolve_group(aprent, info, id_from_token):
        pass


class Search(Interface):
    class Meta:
        description = "Union returning search of Wishlists, Items and Users"
        types = (Wishlist, Item, User)

    title = String()
    id = ID()

    def resolve_type(cls, instance, info):
        pass


class UsersWishlistsAndItems(Interface):
    class Meta:
        description = "Union returning Wishlists and Items of User"
        types = (Wishlist, Item)

    title = String()
    id = ID()

    def resolve_type(cls, instance, info):
        pass

