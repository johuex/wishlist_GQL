from graphene import ObjectType, Mutation, ID, Boolean, String, InputObjectType, Date, Argument, List
from app.auth import token_required, token_check
from app.database import db_session as db
from app.models import Group, GroupUser, GroupList, ItemGroup, GroupAccessEnum, RoleEnum, Item, Wishlist
from app.schema import Group as GroupQl, GroupUser as GroupUserQl, Item as ItemQl, Wishlist as WishlistQl
from datetime import datetime


class AddGroupInput(InputObjectType):
    """Input for add group"""
    title = String(required=True)
    about = String()
    access_level = Argument(GroupQl._meta.fields['access_level'].type)
    date = Date(required=True)
    admin_role = Argument(GroupUserQl._meta.fields['role_in_group'].type, description='The group model will depend on the role of the administrator')


class EditGroupInput(InputObjectType):
    """Input for editing group"""
    group_id = ID(requiered=True)
    title = String()
    about = String()
    access_level = Argument(GroupQl._meta.fields['access_level'].type)
    date = Date()


class AddGroup(Mutation):
    class Arguments:
        data = AddGroupInput(required=True)

    ok = Boolean()
    message = String()
    ID = ID()

    @token_required
    def mutate(self, info, data, id_from_token):
        a_level = GroupAccessEnum(data.access_level)
        role = RoleEnum(data.admin_role)
        new_group = Group(title=data.title, about=data.about, access_level=a_level, date_creation=datetime.utcnow(),
                     date=data.date, admin_id=id_from_token)
        db.add(new_group)
        db.commit()
        db.refresh(new_group)
        db.add(GroupUser(group_id=new_group.id, user_id=id_from_token, role_in_group=role))
        db.commit()
        return AddGroup(ok=True, message="Group has been added!", ID=new_group.id)


class EditGroup(Mutation):
    class Arguments:
        data = EditGroupInput(required=True)

    ok = Boolean()
    message = String()

    @token_required
    def mutate(self, info, data, id_from_token):
        group = db.query(Group).filter_by(id=data.group_id).first()
        if int(group.admin_id) != id_from_token:
            return EditGroup(ok=False, message="Access denied!")
        if data.title is not None and data.title != group.title:
            group.title = data.title
        if data.about is not None and data.about != group.about:
            group.about = data.about
        if data.access_level is not None and data.access_level != group.access_level:
            group.access_level = GroupAccessEnum(data.access_level)
        db.commit()
        return EditGroup(ok=True, message="Item edited!")


class DeleteGroup(Mutation):
    class Arguments:
        group_id = ID(required=True)

    ok = Boolean()
    message = String()

    @token_check
    def mutate(self, info, group_id, id_from_token):
        group = db.query(Group).filter_by(id=group_id).first()
        if group.admin_id != id_from_token:
            return DeleteGroup(ok=False, message="Access denied!")
        db.delete(group)
        db.commit()
        return EditGroup(ok=True, message="Group was deleted!")


class AddItems(Mutation):
    class Arguments:
        group_id = ID(required=True)
        items_id = List(ID)

    ok = Boolean()
    message = String()

    @token_check
    def mutate(self, info, group_id, items_id, id_from_token):
        group = db.query(Group).filter_by(id=group_id).first()
        admin_role = db.query(GroupUser.role_in_group).filter_by(user_id=group.admin_id, group_id=group_id).first()
        user_role = db.query(GroupUser.role_in_group).filter_by(user_id=id_from_token, group_id=group_id).first()
        if admin_role.role_in_group == RoleEnum.FRIENDS:
            if user_role.role_in_group is not None and user_role.role_in_group == RoleEnum.FRIENDS:
                for item_id in items_id:
                    i = db.query(Item).filter_by(id=item_id).first()
                    if i.owner_id == id_from_token:
                        db.add(ItemGroup(group_id=group_id, item_id=item_id))
                    db.commit()
                return AddItems(ok=True, message="Items have been added!")
        if admin_role.role_in_group == RoleEnum.ORGANIZER:
            if user_role.role_in_group is not None and user_role.role_in_group == RoleEnum.ORGANIZER:
                for item_id in items_id:
                    i = db.query(Item).filter_by(id=item_id).first()
                    if i.owner_id == id_from_token:
                        db.add(ItemGroup(group_id=group_id, item_id=item_id))
                db.commit()
                return AddItems(ok=True, message="Items have been added!")

        return AddItems(ok=False, message="Access denied!")


class AddLists(Mutation):
    class Arguments:
        group_id = ID(required=True)
        lists_id = List(ID)

    ok = Boolean()
    message = String()

    @token_check
    def mutate(self, info, group_id, lists_id, id_from_token):
        group = db.query(Group).filter_by(id=group_id).first()
        admin_role = db.query(GroupUser.role_in_group).filter_by(user_id=group.admin_id, group_id=group_id).first()
        user_role = db.query(GroupUser.role_in_group).filter_by(user_id=id_from_token, group_id=group_id).first()
        if admin_role == RoleEnum.FRIENDS:
            if user_role is not None and user_role == RoleEnum.FRIENDS:
                for list_id in lists_id:
                    i = db.query(Wishlist).filter_by(id=list_id).first()
                    if i.user_id == id_from_token:
                        db.add(GroupList(group_id=group_id, wishlist_id=list_id))
                db.commit()
                return AddLists(ok=True, message="WishLists have been added!")
        if admin_role == RoleEnum.ORGANIZER:
            if user_role is not None and user_role == RoleEnum.ORGANIZER:
                for list_id in lists_id:
                    i = db.query(Item).filter_by(id=list_id).first()
                    if i.user_id == id_from_token:
                        db.add(GroupList(group_id=group_id, wishlist_id=list_id))
                db.commit()
                return AddLists(ok=True, message="WishLists have been added!")

        return AddLists(ok=True, message="Access denied!")


class AddUsers(Mutation):
    """Add GUESTS or FRIENDS to Group; for add ORGANIZATOR look at AddOrganizer"""
    class Arguments:
        group_id = ID(required=True)
        users_id = List(ID)

    ok = Boolean()
    message = String()

    @token_check
    def mutate(self, info, group_id, users_id, id_from_token):
        group = db.query(Group).filter_by(id=group_id).first()
        admin_role = db.query(GroupUser.role_in_group).filter_by(user_id=group.admin_id, group_id=group_id).first()
        user_role = db.query(GroupUser.role_in_group).filter_by(user_id=id_from_token, group_id=group_id).first()
        if admin_role == RoleEnum.FRIENDS:
            if user_role is not None and user_role == RoleEnum.FRIENDS:
                for user_id in users_id:
                    db.add(GroupUser(group_id=group_id, user_id=user_id, role_in_group=admin_role))
                db.commit()
                return AddUsers(ok=True, message="Users have been added!")
        if admin_role == RoleEnum.ORGANIZER:
            if user_role is not None and user_role == RoleEnum.ORGANIZER:
                for user_id in users_id:
                    db.add(GroupUser(group_id=group_id, user_id=user_id, role_in_group=RoleEnum.GUEST))
                db.commit()
                return AddUsers(ok=True, message="Users have been added!")

        return AddUsers(ok=True, message="Access denied!")


class AddOrganizer(Mutation):
    class Arguments:
        group_id = ID(required=True)
        user_id = ID(required=True)

    ok = Boolean()
    message = String()

    @token_check
    def mutate(self, info, group_id, user_id, id_from_token):
        group = db.query(Group).filter_by(id=group_id).first()
        admin_role = db.query(GroupUser.role_in_group).filter_by(user_id=group.admin_id, group_id=group_id).first()
        user_role = db.query(GroupUser.role_in_group).filter_by(user_id=id_from_token, group_id=group_id).first()
        if admin_role == RoleEnum.ORGANIZER:
            if user_role is not None and user_role == RoleEnum.ORGANIZER:
                db.add(GroupUser(group_id=group_id, user_id=user_id, role_in_group=RoleEnum.ORGANIZER))
                db.commit()
                return AddOrganizer(ok=True, message="Users have been added!")

        return AddOrganizer(ok=True, message="Only admin with role ORGANIZER can add ORGANIZER!")


class GroupMutation(ObjectType):
    add_group = AddGroup.Field()
    edit_group = EditGroup.Field()
    delete_group = DeleteGroup.Field()
    add_items_to_group = AddItems.Field()
    add_lists_to_group = AddLists.Field()
    add_users_to_group = AddUsers.Field()
    add_organizer = AddOrganizer.Field()
