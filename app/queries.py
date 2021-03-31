from graphene import ObjectType, relay
from graphene_sqlalchemy import SQLAlchemyConnectionField
from .schema import User
from .database import SessionLocal


class Query(ObjectType):
    node = relay.Node.Field()
    all_users = SQLAlchemyConnectionField(User.connection)

    async def resolve_all_users(self, info, name):
        # We can make asynchronous network calls here.
        return "Hello " + name