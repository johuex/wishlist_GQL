from graphene import ObjectType, Mutation, String, Boolean, Enum, ID, InputObjectType, List, Argument, Field
from graphene_file_upload.scalars import Upload
from app.models import Item, ItemPicture, DegreeEnum, AccessLevelEnum, StatusEnum, User
from app.schema import Item as ItemQl, User as UserQl
from app.database import db_session as db, commit_with_check
from app.auth import token_required, last_seen_set, token_check
from datetime import datetime
from app.s3 import *
from app.config import Config


class ItemAddInput(InputObjectType):
    """Input for add item"""
    title = String(required=True)
    about = String()
    access_level = Argument(ItemQl._meta.fields['access_level'].type)
    list_id = ID()
    degree = Argument(ItemQl._meta.fields['degree'].type)


class ItemEditInput(InputObjectType):
    """Input for edit item"""
    item_id = ID()
    title = String()
    about = String()
    access_level = Argument(ItemQl._meta.fields['access_level'].type)
    list_id = ID()
    degree = Argument(ItemQl._meta.fields['degree'].type)


class AddItem(Mutation):
    class Arguments:
        data = ItemAddInput(required=True)

    ok = Boolean()
    message = String()
    ID = ID()

    @token_required
    @last_seen_set
    def mutate(root, info, data, id_from_token):
        degree = DegreeEnum.NOTSTATED
        a_level = AccessLevelEnum(data.access_level)
        if data.degree is not None:
            degree = DegreeEnum(data.degree)
        new_item = Item(title=data.title, owner_id=id_from_token, about=data.about, access_level=a_level,
                    list_id=data.list_id, degree=degree, status='FREE', date_for_status=datetime.utcnow(),
                    date_creation=datetime.utcnow())
        try:
            db.add(new_item)
            commit_with_check(db)
        except:
            db.rollback()
        db.refresh(new_item)
        try:
            db.add(ItemPicture(item_id=new_item.id, path_to_picture='items/item_0.png'))
            commit_with_check(db)
        except:
            db.rollback()
        return AddItem(ok=True, message="Item added!", ID=new_item.id)


class EditItem(Mutation):
    class Arguments:
        data = ItemEditInput(required=True)

    ok = Boolean()
    message = String()
    edited_item = Field(lambda: ItemQl)

    @token_required
    @last_seen_set
    def mutate(root, info, data, id_from_token):
        item = db.query(Item).filter_by(id=data.item_id).first()
        if item is None:
            raise Exception("No item was found with this ID!")
        if int(item.owner_id) != id_from_token:
            return EditItem(ok=False, message="Access denied!")
        if data.title is not None and data.title != item.title:
            item.title = data.title
        if data.about is not None and data.about != item.about:
            item.about = data.about
        if data.access_level is not None and data.access_level != item.access_level:
            item.access_level = AccessLevelEnum(data.access_level)
        if data.list_id is not None and data.list_id != item.list_id:
            item.list_id = data.list_id
        if data.degree is not None and data.degree != item.degree:
            item.degree = AccessLevelEnum(data.degree)
        commit_with_check(db)
        return EditItem(ok=True, message="Item edited!", edited_item=item)


class DeleteItem(Mutation):
    class Arguments:
        item_id = ID()

    ok = ID()
    message = String()

    @token_check
    def mutate(self, info, item_id, id_from_token):
        item = db.query(Item).filter_by(id=item_id).first()
        if item is None:
            raise Exception("No item was found with this ID!")
        if item.owner_id != id_from_token:
            return DeleteItem(ok=False, message="Access denied!")
        # TODO если не работают Cascade, то нужно удалять в остальных таблицах вручную
        try:
            db.delete(item)
            commit_with_check(db)
        except:
            db.rollback()
        return DeleteItem(ok=True, message="Item deleted!")


class AddPictures(Mutation):
    class Arguments:
        files = List(Upload)
        item_id = ID(required=True)

    ok = Boolean()
    message = String()

    @token_check
    def mutate(self, info, files,  item_id, id_from_token):
        item = db.query(Item).filter_by(id=item_id).first()
        if item is None:
            raise Exception("No item was found with this ID!")
        if item.owner_id != id_from_token:
            return AddPictures(ok=False, message="Access denied!")
        # TODO maybe change names for pictures?
        i = 0
        for pic in files:
            if check_format(pic):
                i += 1
                name = 'items/item_'+str(item.id)+'_'+str(i)
                if upload_file(pic, Config.bucket, name):
                    try:
                        db.add(ItemPicture(item_id=item.id, path_to_picture=name))
                        commit_with_check(db)
                    except:
                        db.rollback()
                else:
                    return AddPictures(ok=False, message="Pictures haven't been uploaded!")
            else:
                return AddPictures(ok=False, message="Only pictures (.png, .jpeg, .bmp) can be downloaded!")
        return AddPictures(ok=True, messages="Pictures have been uploaded!")


class RemovePictures(Mutation):
    class Arguments:
        urls = List(String)

    ok = Boolean()
    message = String()

    @token_check
    def mutate(self, info, urls, id_from_token):
        if len(urls) == 0:
            return RemovePictures(ok=False, message="No URLs to delete pictures!")
        for pic in urls:
            item_path = db.query(ItemPicture).filter_by(path_to_picture=pic).first()
            item = db.query(Item).filter_by(id=item_path.item_id).first()
            if item.owner_id != id_from_token:
                raise Exception("Access denied!")
            if delete_file(Config.bucket, item_path.path_to_picture):
                try:
                    db.delete(item_path)
                    commit_with_check(db)
                except:
                    db.rollback()
        return RemovePictures(ok=True, message="Pictures have been deleted!")


class SetGiverId(Mutation):
    class Arguments:
        item_id = ID(required=True)

    ok = Boolean()
    message = String()
    user_ = Field(lambda: UserQl)

    @token_check
    def mutate(self, info, item_id, id_from_token):
        item = db.query(Item).filter_by(id=item_id).first()
        if item is None:
            raise Exception("No item was found with this ID!")
        if item.giver_id is not None:
            return SetGiverId(ok=False, message="This item has already reserved!")
        if item.status == StatusEnum.PERFORMED:
            raise Exception("This item is already performed!")
        if item.status == StatusEnum.RESERVED:
            if item.giver_id == id_from_token:
                # cancel reservation by giver_id user
                item.giver_id = None
                commit_with_check(db)
                user = db.query(User).filter_by(id=item.owner_id).first()
                return SetGiverId(ok=True, message="Reserving of item is canceled!!", user_=user)
            else:
                raise Exception("This item is already reserved!")
        item.giver_id = id_from_token
        item.status = StatusEnum.RESERVED
        commit_with_check(db)
        user = db.query(User).filter_by(id=item.owner_id).first()
        return SetGiverId(ok=True, message="Item was reserved!!", user_=user)


class ItemPerformed(Mutation):
    class Arguments:
        item_id = ID(required=True)

    ok = Boolean()
    message = String()

    @token_check
    def mutate(self, info, item_id, id_from_token):
        item = db.query(Item).filter_by(id=item_id).first()
        if item is None:
            raise Exception("No item was found with this ID!")
        if item.owner_id != id_from_token:
            return ItemPerformed(ok=False, message="Access denied!!")
        if item.status == StatusEnum.PERFORMED:
            raise Exception("This item is already performed!")
        item.status = StatusEnum.PERFORMED
        item.list_id = None
        commit_with_check(db)
        return ItemPerformed(ok=True, message="Item was performed!")


class ItemMutation(ObjectType):
    add_item = AddItem.Field()
    edit_item = EditItem.Field()
    delete_item = DeleteItem.Field()
    add_pictures = AddPictures.Field()
    remove_pictures = RemovePictures.Field()
    set_giver_id = SetGiverId.Field()
    item_performed = ItemPerformed.Field()

