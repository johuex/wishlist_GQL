from graphene import ObjectType, relay, Field, ID, List, String
from app.schema import User as UserQl, Wishlist as WishlistQl, Item as ItemQl, Group as GroupQl, Search as SearchQL, \
    UsersWishlistsAndItems as WaIQL
from app.models import User as UserDB, Wishlist as WishlistDB, Item as ItemDB, Group as GroupDB,\
    FriendShip as FSDB, AccessLevelEnum, GroupAccessEnum, GroupUser as GroupUserDB
from app.database import db_session as db
from app.auth import token_check, last_seen_set
from sqlalchemy import and_, or_


class Query(ObjectType):
    class Meta:
        exclude_fields = ('users', 'wishlists', 'items', 'groups')
    node = relay.Node.Field()
    me = Field(UserQl, description="Return yourself by ID from token")
    user = Field(UserQl, user_id=ID(required=True), description="Return user by ID")
    wishlist = Field(WishlistQl, list_id=ID(required=True), description="Return wishlist by ID")
    item = Field(ItemQl, item_id=ID(required=True), description="Return item by ID")
    group = Field(GroupQl, group_id=ID(required=True), description="Return group by ID")
    news = Field(lambda: List(WaIQL), description="News from friends of user")
    index = Field(lambda: List(WaIQL), description="All open items and wishlists of all users on this service")
    search = Field(lambda: List(SearchQL), search_text=String(required=True), description="Search in users, items, wishlists, groups")

    @token_check
    @last_seen_set
    async def resolve_me(parent, info, id_from_token):
        return db.query(UserDB).filter_by(id=int(id_from_token)).first()

    @last_seen_set
    async def resolve_user(parent, info, user_id):
        return db.query(UserDB).filter_by(id=int(user_id)).first()

    @token_check
    @last_seen_set
    async def resolve_wishlist(parent, info, list_id, id_from_token):
        wishlist = db.query(WishlistDB).filter_by(id=int(list_id)).first()
        if wishlist.access_level == AccessLevelEnum.ALL:
            return wishlist
        if wishlist.access_level == AccessLevelEnum.NOBODY and wishlist.user_id == id_from_token:
            return wishlist
        if wishlist.access_level == AccessLevelEnum.FRIENDS and db.query(FSDB).filter_by(user_id_1=wishlist.user_id,
                                                                       user_id_2=id_from_token).first():
            return wishlist
        raise Exception("Access denied!")

    @token_check
    @last_seen_set
    async def resolve_item(parent, info, item_id, id_from_token):
        item = db.query(ItemDB).filter_by(id=int(item_id)).first()
        if item.access_level == AccessLevelEnum.ALL:
            return item
        if item.access_level == AccessLevelEnum.NOBODY and item.owner_id == id_from_token:
            return item
        if item.access_level == AccessLevelEnum.FRIENDS and db.query(FSDB).filter_by(user_id_1=item.owner_id,
                                                                       user_id_2 = id_from_token).first():
            return item
        raise Exception("Access denied!")

    @token_check
    @last_seen_set
    async def resolve_group(parent, info, group_id, id_from_token):
        group = db.query(GroupDB).filter_by(id=group_id).first()
        if group.access_level == GroupAccessEnum.OPEN:
            return group
        user_group = db.query(GroupUserDB).filter_by(user_id=id_from_token, group_id=group_id).first()
        if group.access_level == GroupAccessEnum.CLOSE and user_group is not None:
            return group
        raise Exception("Access denied!")

    @token_check
    @last_seen_set
    def resolve_news(parent, info, id_from_token):
        wishlists = db.query(WishlistDB)\
            .join(WishlistDB.user_owner)\
            .join(UserDB.friends)\
            .filter(and_(UserDB.id == id_from_token, or_((WishlistDB.access_level == 'ALL'), (WishlistDB.access_level == 'FRIENDS'))))\
            .all()
        items = db.query(ItemDB)\
            .join(ItemDB.owner)\
            .join(UserDB.friends) \
            .filter(and_(UserDB.id == id_from_token,
                         or_((ItemDB.access_level == 'ALL'), (ItemDB.access_level == 'FRIENDS'))))\
            .all()
        return items + wishlists

    @last_seen_set
    def resolve_index(parent, info):
        wishlists = db.query(WishlistDB) \
            .join(WishlistDB.user_owner) \
            .join(UserDB.friends) \
            .filter(WishlistDB.access_level == 'ALL') \
            .all()
        items = db.query(ItemDB) \
            .join(ItemDB.owner) \
            .join(UserDB.friends) \
            .filter(ItemDB.access_level == 'ALL') \
            .all()
        return items + wishlists

    @token_check
    @last_seen_set
    def resolve_search(parent, info, search_text, id_from_token):
        string_list = search_text.split(" ")
        items = list()
        wishlists = list()
        users = list()
        for i in string_list:
            temp = db.query(UserDB).filter_by(nickname=i).first()
            if temp is not None:
                users.append(temp)
            temp = db.query(UserDB).filter_by(user_name=i).first()
            if temp is not None:
                users.append(temp)
            temp = db.query(UserDB).filter_by(surname=i).first()
            if temp is not None:
                users.append(temp)

            temp = db.query(WishlistDB).filter_by(title=i, access_level='ALL').all()
            if len(temp) != 0:
                for j in temp:
                    items.append(j)
            temp = db.query(ItemDB).filter_by(title=i, access_level='ALL').all()
            if len(temp) != 0:
                for j in temp:
                    items.append(j)
        return items + wishlists + users
