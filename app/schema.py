"""GQL Schema description"""
from graphene import relay, Union, Enum, Interface, String, ID
from app.models import User as UserModel, FriendRequests as FriendRequestsModel, FriendShip as FriendShipModel,\
    Item as ItemModel, Group as GroupModel, Wishlist as WishlistModel,\
    ItemPicture as ItemPictureModel, GroupUser as GroupUserModel, GroupList as GroupListModel, \
    ItemGroup as ItemGroupModel, AccessLevelEnum, GroupAccessEnum
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
        responce = list()
        if parent.access_level == AccessLevelEnum.ALL:
            items = db.query(ItemPicture).filter_by(item_id=parent.id).all()
            for pic in items:
                responce.append(download_file(Config.bucket, pic.path_to_picture))
            return responce
        if parent.access_level == AccessLevelEnum.NOBODY and parent.owner_id == id_from_token:
            items = db.query(ItemPicture).filter_by(item_id=parent.id).all()
            for pic in items:
                responce.append(download_file(Config.bucket, pic.path_to_picture))
            return responce
        if parent.access_level == AccessLevelEnum.FRIENDS and db.query(FriendShipModel).filter_by(user_id_1=parent.owner_id,
                                                                       user_id_2=id_from_token).first():
            items = db.query(ItemPicture).filter_by(item_id=parent.id).all()
            for pic in items:
                responce.append(download_file(Config.bucket, pic.path_to_picture))
            return responce

        return []

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
        return []

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
        results = db.query(GroupUserModel).filter_by(group_id=parent.id).all()
        if parent.access_level == GroupAccessEnum.OPEN:
            return results
        user = db.query(GroupUserModel).filter_by(user_id=id_from_token, group_id=parent.id).first()
        if parent.access_level == GroupAccessEnum.CLOSE and user is not None:
            return results
        return []

    @token_check
    def resolve_items(parent, info, id_from_token):
        results = db.query(ItemGroupModel).filter_by(group_id=parent.id).all()
        if parent.access_level == GroupAccessEnum.OPEN:
            return results
        user = db.query(GroupUserModel).filter_by(user_id=id_from_token, group_id=parent.id).first()
        if parent.access_level == GroupAccessEnum.CLOSE and user is not None:
            return results
        return []

    @token_check
    def resolve_lists(parent, info, id_from_token):
        results = db.query(GroupListModel).filter_by(group_id=parent.id).all()
        if parent.access_level == GroupAccessEnum.OPEN:
            return results
        user = db.query(GroupUserModel).filter_by(user_id=id_from_token, group_id=parent.id).first()
        if parent.access_level == GroupAccessEnum.CLOSE and user is not None:
            return results
        return []


class User(SQLAlchemyObjectType):
    class Meta:
        description = 'Table of Users'
        model = UserModel
        interfaces = (relay.Node,)  # interfaces where Users used
        exclude_fields = ('password_hash', 'token', 'refresh_token', 'users_lists', 'email')

    @token_check
    def resolve_user_lists(parent, info, id_from_token):
        response = list()
        wishlists = db.query(WishlistModel).filter_by(user_id=parent.id).all()
        if len(wishlists) == 0:
            return wishlists
        for wlist in wishlists:
            if wlist.access_level == AccessLevelEnum.ALL:
                response.append(wlist)
            if wlist.access_level == AccessLevelEnum.NOBODY and wlist.user_id == id_from_token:
                response.append(wlist)
            if wlist.access_level == AccessLevelEnum.FRIENDS and db.query(FriendShipModel).filter_by(
                    user_id_1=wlist.user_id,
                    user_id_2=id_from_token).first():
                response.append(wlist)
        if len(response) > 0:
            return response
        return []

    @token_check
    def resolve_friend_requests(parent, info, id_from_token):
        if parent.id == id_from_token:
            return db.query(FriendRequestsModel).filter_by(user_id_to=id_from_token).all()
        return []

    @token_check
    def resolve_friends(parent, info, id_from_token):
        temp = db.query(FriendShipModel).filter_by(user_id_1=parent.id).all()
        return temp.user_id_2


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
        return []

    @token_check
    def resolve_items_giver(parent, info, id_from_token):
        item = db.query(ItemModel).filter_by(owner_id=id_from_token).first()
        if len(item) == 0:
            return item
        if item.giver_id == id_from_token:
            return item
        return []

    def resolve_userpic(parent, info):
        """return url to download picture"""
        user = db.query(UserModel).filter_by(id=parent.id).first()
        return download_file(Config.bucket, user.userpic)

    @token_check
    def resolve_groups(parent, info, id_from_token):
        group_user = db.query(GroupUserModel).filter_by(user_id=parent.id).all()
        if id_from_token == parent.id:
            return group_user
        response = list()
        for i in group_user:
            group = db.query(GroupModel).filter_by(id=i.group_id).first()
            if group.access_level == GroupAccessEnum.OPEN:
                response.append(group)
        return response


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
    def resolve_users(parent, info, id_from_token):
        return db.query(UserModel).filter_by(id=parent.user_id).first()

    @token_check
    def resolve_group(parent, info, id_from_token):
        group = db.query(GroupModel).filter_by(id=parent.group_id).first()
        if parent.user_id == id_from_token or group.access_level == GroupAccessEnum.OPEN:
            return group
        else:
            return []


class GroupList(SQLAlchemyObjectType):
    class Meta:
        description = "Table for lists in groups"
        model = GroupListModel
        interfaces = (relay.Node,)

    @token_check
    def resolve_lists(parent, info, id_from_token):
        return db.query(WishlistModel).filter_by(id=parent.wishlist_id).first()

    @token_check
    def resolve_group(parent, info, id_from_token):
        group = db.query(GroupModel).filter_by(id=parent.group_id).first()
        group_user = db.query(GroupUserModel).filter_by(group_id=parent.group_id).all()
        if id_from_token in group_user.user_id or group.access_level == GroupAccessEnum.OPEN:
            return group
        else:
            return []


class ItemGroup(SQLAlchemyObjectType):
    class Meta:
        description = "Table for items in groups"
        model = ItemGroupModel
        interfaces = (relay.Node,)

    @token_check
    def resolve_item(parent, info, id_from_token):
        return db.query(ItemModel).filter_by(id=parent.item_id).first()

    @token_check
    def resolve_group(parent, info, id_from_token):
        group = db.query(GroupModel).filter_by(id=parent.group_id).first()
        group_user = db.query(GroupUserModel).filter_by(group_id=parent.group_id).all()
        if id_from_token in group_user.user_id or group.access_level == GroupAccessEnum.OPEN:
            return group
        else:
            return []


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

