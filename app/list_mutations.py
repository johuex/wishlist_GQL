from graphene import ObjectType, Mutation, String, Boolean, Argument, ID, InputObjectType, List, Field
from app.models import Wishlist, Item, AccessLevelEnum, StatusEnum
from app.schema import Wishlist as WishlistQl
from app.database import db_session as db, commit_with_check
from app.auth import token_required, last_seen_set, token_check
from app.schema import Wishlist as Listsch


class ListAddInput(InputObjectType):
    """Input for add item"""
    title = String(required=True)
    about = String()
    access_level = Argument(WishlistQl._meta.fields['access_level'].type)


class ListEditInput(InputObjectType):
    """Input for edit item"""
    list_id = ID()
    title = String()
    about = String()
    access_level = Argument(WishlistQl._meta.fields['access_level'].type)


class AddList(Mutation):
    """Add wishlist to user"""
    class Arguments:
        data = ListAddInput(required=True)

    ok = Boolean()
    message = String()
    user_lists = List(WishlistQl)

    @token_required
    @last_seen_set
    def mutate(root, info, data, id_from_token):
        a_level = AccessLevelEnum(data.access_level)
        new_list = Wishlist(title=data.title, user_id=id_from_token, about=data.about, access_level=a_level)
        try:
            db.add(new_list)
            commit_with_check(db)
        except:
            db.rollback()
        db.refresh(new_list)

        lists = db.query(Wishlist).filter_by(user_id=id_from_token)
        return AddList(ok=True, message="Wishlist added!", user_lists=lists)


class EditList(Mutation):
    """Edit wishlist"""
    class Arguments:
        data = ListEditInput(required=True)

    ok = Boolean()
    message = String()
    edited_list = Field(lambda: Listsch)

    @token_required
    @last_seen_set
    def mutate(root, info, data, id_from_token):
        wishlist = db.query(Wishlist).filter_by(id=data.item_id)
        if wishlist is None:
            raise Exception("No wishlist was found with this ID!")
        if wishlist.user_id != id_from_token:
            return EditList(ok=False, message="Access denied!")
        if data.title is not None and data.title != wishlist.title:
            wishlist.title = data.title
        if data.about is not None and data.about != wishlist.about:
            wishlist.about = data.about
        if data.access_level is not None and data.access_level != wishlist.access_level:
            a_level = AccessLevelEnum(data.access_level)
            wishlist.access_level = a_level
            items_in_list = db.query(Item).filter_by(list_id=wishlist.id).all()
            for item in items_in_list:
                item.access_level = a_level
        commit_with_check(db)
        return EditList(ok=True, message="Wishlist edited!", edited_list=wishlist)


class DeleteWishList(Mutation):
    """Delete wishlist with items or paste them in default wishlist"""
    class Arguments:
        list_id = ID()
        with_items = Boolean()

    ok = Boolean()
    message = String()

    @token_check
    def mutate(self, info, list_id, id_from_token, with_items):
        wlist = db.query(Wishlist).filter_by(id=list_id).first()
        if wlist is None:
            raise Exception("No wishlist with this ID found!")
        if wlist.user_id != id_from_token:
            return DeleteWishList(ok=False, message="Access denied!")
        if with_items:
            # TODO если не работают Cascade, то нужно удалять в остальных таблицах вручную
            try:
                db.delete(wlist)
                commit_with_check(db)
            except:
                db.rollback()
            return DeleteWishList(ok=True, message="Wishlist deleted with items!")
        else:
            items_in_list = db.query(Item).filter_by(list_id=list_id).all()
            for item in items_in_list:
                item.list_id = None
            return DeleteWishList(ok=True, message="Wishlist was deleted! Items are in default wishlist")


class AddItemsToList(Mutation):
    """Add items in wishlist"""
    class Arguments:
        list_id = ID()
        items_id = List(ID)

    ok = Boolean()
    message = String()

    @token_check
    def mutate(self, info, list_id, items_id, id_from_token):
        wlist = db.query(Wishlist).filter_by(id=list_id).first()
        if wlist is None:
            raise Exception("No wishlist with this ID found!")
        if wlist.user_id != id_from_token:
            return AddItemsToList(ok=False, message="Access denied!")
        for item_id in items_id:
            item = db.query(Item).filter_by(id=item_id).first()
            if item.status == StatusEnum.RESERVED or \
               item.status == StatusEnum.PERFORMED or item.owner_id != id_from_token:
                continue
            item.list_id = list_id
            item.access_level = wlist.access_level
            commit_with_check(db)
        return AddItemsToList(ok=True, message="Items were added to wishlist!")


class DeleteItemsFromList(Mutation):
    """Delete items from wishlist and paste them to default wishlist"""
    class Arguments:
        list_id = ID()
        items_id = List(ID)

    ok = Boolean()
    message = String()

    @token_check
    def mutate(self, info, list_id, items_id, id_from_token):
        wlist = db.query(Wishlist).filter_by(id=list_id).first()
        if wlist is None:
            raise Exception("No wishlist with this ID found!")
        if wlist.user_id != id_from_token:
            return DeleteItemsFromList(ok=False, message="Access denied!")
        for item_id in items_id:
            item = db.query(Item).filter_by(id=item_id).first()
            item.list_id = None
            item.access_level = AccessLevelEnum.NOBODY
            commit_with_check(db)
        return DeleteItemsFromList(ok=True, message="Items were deleted from wishlist and were pasted to default wishlist!")


class ListMutation(ObjectType):
    add_list = AddList.Field()
    edit_list = EditList.Field()
    delete_list = DeleteWishList.Field()
    add_items_to_list = AddItemsToList.Field()
    delete_items_from_wishlist = DeleteItemsFromList.Field()
