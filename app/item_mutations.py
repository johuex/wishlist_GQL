from graphene import ObjectType, Mutation, String, Boolean, Enum, ID, InputObjectType, List, Argument
from graphene_file_upload.scalars import Upload
from app.models import Item, ItemPicture, DegreeEnum, AccessLevelEnum, StatusEnum
from app.schema import Item as ItemQl
from app.database import db_session as db
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

    @token_required
    @last_seen_set
    def mutate(root, info, data, id_from_token):
        degree = DegreeEnum.NOTSTATED
        a_level = AccessLevelEnum(data.access_level)
        if data.degree is not None:
            degree = DegreeEnum(data.degree)
        db.add(Item(title=data.title, owner_id=id_from_token, about=data.about, access_level=a_level,
                    list_id=data.list_id, degree=degree, status='FREE', date_for_status=datetime.utcnow(),
                    date_creation=datetime.utcnow()))
        db.commit()
        return AddItem(ok=True, message="Item added!")


class EditItem(Mutation):
    class Arguments:
        data = ItemEditInput(required=True)

    ok = Boolean()
    message = String()

    @token_required
    @last_seen_set
    def mutate(root, info, data, id_from_token):
        item = db.query(Item).filter_by(id=data.item_id).first()
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
        db.commit()
        return EditItem(ok=True, message="Item edited!")


class DeleteItem(Mutation):
    class Arguments:
        item_id = ID()
        owner_id = ID()

    ok = ID()
    message = String()

    @token_check
    def mutate(self, info, item_id, owner_id, id_from_token):
        if int(owner_id) != id_from_token:
            return DeleteItem(ok=False, message="Access denied!")
        item = db.query(Item).filter_by(id=item_id).first()
        # TODO если не работают Cascade, то нужно удалять в остальных таблицах вручную
        db.delete(item)
        db.commit()


class AddPictures(Mutation):
    class Arguments:
        files = List(Upload)
        item_id = ID(required=True)

    ok = Boolean()
    message = String()

    @token_check
    def mutate(self, info, files,  item_id, id_from_token):
        item = db.query(Item).filter_by(id=item_id).first()
        if item.owner_id != id_from_token:
            return AddPictures(ok=False, message="Access denied!")
        pictures = info.context.FILES
        for pic in pictures:
            i = 0
            if check_format(pic):
                i += 1
                name = 'item_'+str(item.id)+str(i)
                url = f"https://" + Config.bucket + "s3.amazonaws.com" + name
                upload_file(pic, Config.bucket, name)
                db.add(ItemPicture(item_id=item.id, path_to_picture=name))
                db.commit()
        return AddPictures(ok=True, messages="Pictures have been uploaded!")


class RemovePictures(Mutation):
    class Arguments:
        url = String(required=True)

    ok = Boolean()
    message = String()

    @token_check
    def mutate(self, info, url):
        pass


class SetGiverId(Mutation):
    class Arguments:
        item_id = ID(required=True)

    ok = Boolean()
    message = String()

    @token_check
    def mutate(self, info,item_id, id_from_token):
        item = db.query(Item).filter_by(id=item_id).first()
        if item.giver_id is not None:
            return SetGiverId(ok=False, message="This item has already reserved!")
        item.giver_id = id_from_token
        item.status = StatusEnum.RESERVED
        db.commit()
        return SetGiverId(ok=True, message="Item was reserved!!")


class ItemPerformed(Mutation):
    class Arguments:
        item_id = ID(required=True)

    @token_check
    def mutate(self, info, item_id, id_from_token):
        item = db.query(Item).filter_by(id=item_id).first()
        if item.owner_id != id_from_token:
            return ItemPerformed(ok=False, message="Access denied!!")
        item.status = StatusEnum.PERFORMED
        db.commit()
        return ItemPerformed(ok=True, message="Item was performed!")


class ItemMutation(ObjectType):
    add_item = AddItem.Field()
    edit_item = EditItem.Field()
    delete_item = DeleteItem.Field()
    add_pictures = AddPictures.Field()
    remove_pictures = AddPictures.Field()
    set_giver_id = SetGiverId.Field()
    item_performed = ItemPerformed.Field()

