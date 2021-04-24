from graphene import ObjectType, relay, Field, ID, String
from app.schema import User as UserQl, Wishlist as WishlistQl, Item as ItemQl, Group as GroupQl
from app.models import User as UserDB, Wishlist as WishlistDB, Item as ItemDB, Group as GroupDB,\
    FriendShip as FSDB
from app.database import db_session as db
from app.auth import token_check, last_seen_set


class Query(ObjectType):
    class Meta:
        exclude_fields = ('users', 'wishlists', 'items', 'groups')
    node = relay.Node.Field()
    user = Field(UserQl, user_id=ID(required=True), description="Return user by ID")
    wishlist = Field(WishlistQl, list_id=ID(required=True), description="Return wishlist by ID")
    item = Field(ItemQl, item_id=ID(required=True), description="Return item by ID")
    group = Field(GroupQl, group_id=ID(required=True), description="Return group by ID")
    '''
    # it's an example for working with token
    async def resolve_user(parent, info, user_id, token):
        """return user by id"""
        id_from_token = int(au.decode_token(token))
        if int(user_id) == id_from_token:
            return db.query(UserDB).filter_by(id=user_id).first()
        else:
            # TODO сделать грамотный вывод об ошибке в ???
            return error_response(401, 'Access denied')
    '''

    @last_seen_set
    async def resolve_user(parent, info, user_id):
        return db.query(UserDB).filter_by(id=int(user_id)).first()

    @token_check
    @last_seen_set
    async def resolve_wishlist(parent, info, list_id, id_from_token):
        wishlist = db.query(WishlistDB).filter_by(id=int(list_id)).first()
        if wishlist.access_level == 'ALL':
            return wishlist
        if wishlist.access_level == 'NOBODY' and wishlist.user_id == id_from_token:
            return wishlist
        if wishlist.access_level == 'FRIENDS' and db.query(FSDB).filter_by(user_id_1=wishlist.user_id,
                                                                       user_id_2=id_from_token).first():
            return wishlist
        raise Exception("Access denied!")

    @token_check
    @last_seen_set
    async def resolve_item(parent, info, item_id, id_from_token):
        item = db.query(ItemDB).filter_by(id=int(item_id)).first()
        if item.access_level == 'ALL':
            return item
        if item.access_level == 'NOBODY' and item.owner_id == id_from_token:
            return item
        if item.access_level == 'FRIENDS' and db.query(FSDB).filter_by(user_id_1=item.owner.id,
                                                                       user_id_2 = id_from_token).first():
            return item
        raise Exception("Access denied!")

    @token_check
    @last_seen_set
    async def resolve_group(parent, info, group_id, id_from_token):
        pass
