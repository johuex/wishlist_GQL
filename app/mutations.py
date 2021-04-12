from app.user_mutations import UserMutation
from app.item_mutations import ItemMutation
from app.list_mutations import ListMutation


class Mutation(UserMutation, ItemMutation, ListMutation):
    pass
