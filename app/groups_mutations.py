from graphene import ObjectType, Mutation, ID, Boolean, String, InputObjectType, Date, Argument
from app.auth import token_required
from app.database import db_session as db
from app.models import Group, GroupUser, GroupList, ItemGroup
from app.schema import Group as GroupQl
from datetime import datetime


class AddGroupInput(InputObjectType):
    """Input for add group"""
    title = String(required=True)
    about = String()
    access_level = Argument(GroupQl._meta.fields['access_level'].type)
    date = Date()


class AddGroup(Mutation):
    class Arguments:
        data = AddGroupInput(required=True)

    ok = Boolean()
    message = String()

    @token_required
    def mutate(self, info, data, id_from_token):
        new_group_id = db.add(Group(title=data.title, about=data.about, access_level=data.access_level, date_creation=datetime.utcnow(),
                     date=data.date))
        db.add(GroupUser(group_id=new_group_id, user_id=id_from_token, role_in_group='ORGANIZER'))
        return AddGroup(ok=True, message="Group has been added!")


class EditGroup(Mutation):
    class Arguments:
        pass

    ok = Boolean()
    message = String()

    def mutate(self, info, data):
        pass


class DeleteGroup(Mutation):
    class Arguments:
        pass

    ok = Boolean()
    message = String()

    def mutate(self, info, data):
        pass


class AddItems(Mutation):
    class Arguments:
        pass

    ok = Boolean()
    message = String()

    def mutate(self, info, data):
        pass


class AddLists(Mutation):
    class Arguments:
        pass

    ok = Boolean()
    message = String()

    def mutate(self, info, data):
        pass


class AddUsers(Mutation):
    class Arguments:
        pass

    ok = Boolean()
    message = String()

    def mutate(self, info, data):
        pass


class EditRoles(Mutation):
    class Arguments:
        pass

    ok = Boolean()
    message = String()

    def mutate(self, info, data):
        pass


class GroupMutation(ObjectType):
    add_group = AddGroup.Field()
    edit_group = EditGroup.Field()
    delete_group = DeleteGroup.Field()
    add_items_to_group = AddItems.Field()
    add_lists_to_group = AddLists.Field()
    add_users_to_group = AddUsers.Field()
    edit_roles = EditRoles.Field()
