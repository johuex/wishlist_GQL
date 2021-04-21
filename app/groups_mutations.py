from graphene import ObjectType, Mutation, ID, Boolean, String


class AddGroup(Mutation):
    class Arguments:
        pass

    ok = Boolean()
    message = String()

    def mutate(self, info, data):
        pass


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
