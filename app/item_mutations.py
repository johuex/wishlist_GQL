from graphene import ObjectType, Mutation, String, Boolean, Enum, ID, InputObjectType, List
from graphene_file_upload.scalars import Upload
from app.models import Item, AccessLevelEnum, StatusEnum, DegreeEnum
from app.database import db_session as db
from app.auth import token_required, last_seen_set, token_check
from datetime import datetime
import boto3


class ItemAddInput(InputObjectType):
    """Input for add item"""
    title = String(required=True)
    about = String()
    access_level = Enum.from_enum(AccessLevelEnum)
    list_id = ID()
    degree = Enum.from_enum(DegreeEnum)
    token = String()


class ItemEditInput(InputObjectType):
    """Input for edit item"""
    item_id = ID()
    owner_id = ID()
    title = String()
    about = String()
    access_level = String()
    list_id = ID()
    degree = String()
    token = String()


class AddItem(Mutation):
    class Arguments:
        data = ItemAddInput(required=True)

    ok = Boolean()
    message = String()

    @token_required
    @last_seen_set
    def mutate(root, info, data, id_from_token):
        if data.degree is None:
            data.degree = "NOT_STATED"

        db.add(Item(title=data.title, owner_id=id_from_token, about=data.about, access_level=data.access_level,
                    list_id=data.list_id, degree=data.degree, status='FREE', date_for_status=datetime.utcnow(),
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
        if int(data.owner_id) != id_from_token:
            return EditItem(ok=False, message="Access denied!")
        item = db.query(Item).filter_by(id=data.item_id).first()
        if data.title is not None and data.title != item.title:
            item.title = data.title
        if data.about is not None and data.about != item.about:
            item.about = data.about
        if data.access_level is not None and data.access_level != item.access_level:
            item.access_level = data.access_level
        if data.list_id is not None and data.list_id != item.list_id:
            item.list_id = data.list_id
        if data.degree is not None and data.degree != item.degree:
            item.degree = data.degree
        db.commit()
        return EditItem(ok=True, message="Item edited!")


class DeleteItem(Mutation):
    class Arguments:
        item_id = ID()
        owner_id = ID()
        token = String()

    ok = ID()
    message = String()

    @token_check
    def mutate(self, info, item_id, owner_id, token, id_from_token):
        if int(owner_id) != id_from_token:
            return DeleteItem(ok=False, message="Access denied!")
        item = db.query(Item).filter_by(id=item_id).first()
        # TODO если не работают Cascade, то нужно удалять в остальных таблицах вручную
        db.delete(item)
        db.commit()


class AddPictures(Mutation):
    class Arguments:
        files = List(Upload(required=True))
        token = String(required=True)
        item_id = ID(required=True)

    ok = Boolean()
    message = String()

    @token_check
    def mutate(self, info, files, token, item_id, id_from_token):
        item = db.query(Item).filter_by(id=item_id).first()
        if item.owner_id != id_from_token:
            return AddPictures(ok=False, message="Access denied!")
        s3 = boto3.resource('s3')
        for pic in files:
            s3.Bucket('4742').put_object(Key='название файла', Body=pic)


class ItemMutation(ObjectType):
    add_item = AddItem.Field()
    edit_item = EditItem.Field()
    delete_item = DeleteItem.Field()
    add_pictures = AddPictures.Field()
    remove_pictures = AddPictures.Field()

