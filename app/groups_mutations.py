from graphene import ObjectType, Mutation, ID, Boolean, String, InputObjectType, Date, Argument, List, Field
from app.auth import token_required, token_check
from app.database import db_session as db, commit_with_check
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
        try:
            db.add(new_group)
            commit_with_check(db)
        except:
            db.rollback()
        db.refresh(new_group)
        try:
            db.add(GroupUser(group_id=new_group.id, user_id=id_from_token, role_in_group=role))
            commit_with_check(db)
        except:
            db.rollback()
        return AddGroup(ok=True, message="Group has been added!", ID=new_group.id)


class EditGroup(Mutation):
    class Arguments:
        data = EditGroupInput(required=True)

    ok = Boolean()
    message = String()
    edited_group = Field(lambda: GroupQl)

    @token_required
    def mutate(self, info, data, id_from_token):
        data.group_id = int(data.group_id)
        data.admin_id = int(data.admin_id)
        group = db.query(Group).filter_by(id=data.group_id).first()
        if group is None:
            raise Exception("No group with this ID found!")
        if group.admin_id != id_from_token:
            return EditGroup(ok=False, message="Access denied!")
        if data.title is not None and data.title != group.title:
            group.title = data.title
        if data.about is not None and data.about != group.about:
            group.about = data.about
        if data.access_level is not None and data.access_level != group.access_level:
            group.access_level = GroupAccessEnum(data.access_level)
        commit_with_check(db)
        return EditGroup(ok=True, message="Item edited!", edited_group=group)


class DeleteGroup(Mutation):
    class Arguments:
        group_id = ID(required=True)

    ok = Boolean()
    message = String()

    @token_check
    def mutate(self, info, group_id, id_from_token):
        group_id = int(group_id)
        group = db.query(Group).filter_by(id=group_id).first()
        if group is None:
            raise Exception("No group with this ID found!")
        if group.admin_id != id_from_token:
            return DeleteGroup(ok=False, message="Access denied!")
        try:
            db.delete(group)
            commit_with_check(db)
        except:
            db.rollback()
        return EditGroup(ok=True, message="Group was deleted!")


class AddItems(Mutation):
    class Arguments:
        group_id = ID(required=True)
        items_id = List(ID)

    ok = Boolean()
    message = String()

    @token_check
    def mutate(self, info, group_id, items_id, id_from_token):
        group_id = int(group_id)
        items_id = [int(i) for i in items_id]
        group = db.query(Group).filter_by(id=group_id).first()
        if group is None:
            raise Exception("No group with this ID found!")
        admin_role = db.query(GroupUser.role_in_group).filter_by(user_id=group.admin_id, group_id=group_id).first()
        user_role = db.query(GroupUser.role_in_group).filter_by(user_id=id_from_token, group_id=group_id).first()
        if admin_role.role_in_group == RoleEnum.FRIENDS:
            if user_role.role_in_group is not None and user_role.role_in_group == RoleEnum.FRIENDS:
                for item_id in items_id:
                    i = db.query(Item).filter_by(id=item_id).first()
                    if i.owner_id == id_from_token:
                        try:
                            db.add(ItemGroup(group_id=group_id, item_id=item_id))
                            commit_with_check(db)
                        except:
                            db.rollback()
                return AddItems(ok=True, message="Items have been added!")
        if admin_role.role_in_group == RoleEnum.ORGANIZER:
            if user_role.role_in_group is not None and user_role.role_in_group == RoleEnum.ORGANIZER:
                for item_id in items_id:
                    i = db.query(Item).filter_by(id=item_id).first()
                    if i.owner_id == id_from_token:
                        try:
                            db.add(ItemGroup(group_id=group_id, item_id=item_id))
                            commit_with_check(db)
                        except:
                            db.rollback()
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
        group_id = int(group_id)
        lists_id = [int(i) for i in lists_id]
        group = db.query(Group).filter_by(id=group_id).first()
        if group is None:
            raise Exception("No group with this ID found!")
        admin_role = db.query(GroupUser.role_in_group).filter_by(user_id=group.admin_id, group_id=group_id).first()
        user_role = db.query(GroupUser.role_in_group).filter_by(user_id=id_from_token, group_id=group_id).first()
        if admin_role.role_in_group == RoleEnum.FRIENDS:
            if user_role is not None and user_role.role_in_group == RoleEnum.FRIENDS:
                for list_id in lists_id:
                    i = db.query(Wishlist).filter_by(id=list_id).first()
                    if i.user_id == id_from_token:
                        try:
                            db.add(GroupList(group_id=group_id, wishlist_id=list_id))
                            commit_with_check(db)
                        except:
                            db.rollback()
                return AddLists(ok=True, message="WishLists have been added!")
        if admin_role.role_in_group == RoleEnum.ORGANIZER:
            if user_role is not None and user_role.role_in_group == RoleEnum.ORGANIZER:
                for list_id in lists_id:
                    i = db.query(Item).filter_by(id=list_id).first()
                    if i.user_id == id_from_token:
                        try:
                            db.add(GroupList(group_id=group_id, wishlist_id=list_id))
                            commit_with_check(db)
                        except:
                            db.rollback()
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
        group_id = int(group_id)
        users_id = [int(i) for i in users_id]
        group = db.query(Group).filter_by(id=group_id).first()
        if group is None:
            raise Exception("No group with this ID found!")
        admin_role = db.query(GroupUser.role_in_group).filter_by(user_id=group.admin_id, group_id=group_id).first()
        user_role = db.query(GroupUser.role_in_group).filter_by(user_id=id_from_token, group_id=group_id).first()
        if admin_role.role_in_group == RoleEnum.FRIENDS:
            if user_role is not None and user_role.role_in_group == RoleEnum.FRIENDS:
                for user_id in users_id:
                    try:
                        db.add(GroupUser(group_id=group_id, user_id=user_id, role_in_group=admin_role))
                        commit_with_check(db)
                    except:
                        db.rollback()
                return AddUsers(ok=True, message="Users have been added!")
        if admin_role.role_in_group == RoleEnum.ORGANIZER:
            if user_role is not None and user_role.role_in_group == RoleEnum.ORGANIZER:
                for user_id in users_id:
                    try:
                        db.add(GroupUser(group_id=group_id, user_id=user_id, role_in_group=RoleEnum.GUEST))
                        commit_with_check(db)
                    except:
                        db.rollback()
                return AddUsers(ok=True, message="Users have been added!")

        return AddUsers(ok=False, message="Access denied!")


class AddOrganizer(Mutation):
    class Arguments:
        group_id = ID(required=True)
        user_id = ID(required=True)

    ok = Boolean()
    message = String()

    @token_check
    def mutate(self, info, group_id, user_id, id_from_token):
        group_id = int(group_id)
        user_id = int(user_id)
        group = db.query(Group).filter_by(id=group_id).first()
        if group is None:
            raise Exception("No group with this ID found!")
        admin_role = db.query(GroupUser.role_in_group).filter_by(user_id=group.admin_id, group_id=group_id).first()
        user_role = db.query(GroupUser.role_in_group).filter_by(user_id=id_from_token, group_id=group_id).first()
        if admin_role.role_in_group == RoleEnum.ORGANIZER:
            if user_role is not None and user_role.role_in_group == RoleEnum.ORGANIZER:
                try:
                    db.add(GroupUser(group_id=group_id, user_id=user_id, role_in_group=RoleEnum.ORGANIZER))
                    commit_with_check(db)
                except:
                    db.rollback()
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
