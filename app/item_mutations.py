from graphene import ObjectType, Mutation, String, Boolean, Field, ID, InputObjectType
from app.models import Item
from app.database import db_session as db
from app.auth import token_required
from datetime import datetime


class ItemAddInput(InputObjectType):
    """Input for add item"""
    title = String(required=True)
    about = String()
    access_level = String(required=True)
    list_id = ID()
    degree = String()
    token = String()


class ItemEditInput(InputObjectType):
    """Input for edit item"""
    item_id = ID()
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
    def mutate(root, info, data, id_from_token):
        item = db.query(Item).filter_by(id=data.item_id)
        if item.owner_id == id_from_token:
            item.title = data.title
            item.about = data.about
            item.access_level = data.access_level
            item.list_id = data.list_id
            item.degree = data.degree
            db.commit()
        return EditItem(ok=True, message="Item edited!")


class ItemMutation(ObjectType):
    add_item = AddItem.Field()
    edit_item = EditItem.Field()
