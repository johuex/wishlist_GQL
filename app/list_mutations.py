from graphene import ObjectType, Mutation, String, Boolean, Field, ID, InputObjectType
from app.models import Wishlist as List
from app.database import db_session as db
from app.auth import au
from app.schema import AccessLevelEnum, DegreeEnum


class ListAddInput(InputObjectType):
    """Input for add item"""
    title = String(required=True)
    about = String()
    access_level = String(required=True)
    token = String()


class ListEditInput(InputObjectType):
    """Input for edit item"""
    list_id = ID()
    title = String()
    about = String()
    access_level = String()
    token = String()


class AddList(Mutation):
    class Arguments:
        data = ListAddInput(required=True)

    ok = Boolean()
    message = String()

    def mutate(root, info, data):
        id_from_token = int(au.decode_token(data["token"]))
        db.add(List(title=data["title"], user_id=id_from_token, about=data["about"], access_level=data["access_level"]))
        db.commit()
        return AddList(ok=True, message="Wishlist added!")


class EditList(Mutation):
    class Arguments:
        data = ListEditInput(required=True)

    ok = Boolean()
    message = String()

    def mutate(root, info, data):
        id_from_token = int(au.decode_token(data["token"]))
        wishlist = db.query(List).filter_by(id=data["item_id"])
        if wishlist["user_id"] == id_from_token:
            wishlist.title = data["title"]
            wishlist.about = data["about"]
            wishlist.access_level = data["access_level"]
            db.commit()
        return EditList(ok=True, message="Wishlist edited!")


class ListMutation(ObjectType):
    add_list = AddList.Field()
    edit_list = EditList.Field()
