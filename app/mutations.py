from app.user_mutations import UserMutation
from app.item_mutations import ItemMutation
from app.list_mutations import ListMutation
from app.groups_mutations import GroupMutation


class Mutation(UserMutation, ItemMutation, ListMutation, GroupMutation):
    pass
