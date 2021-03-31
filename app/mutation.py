import graphene


class Mutation(graphene.ObjectType):
    hello = graphene.String(
        name=graphene.String(default_value="stranger")
    )

    async def resolve_hello(self, info, name):
        # We can make asynchronous network calls here.
        return "Hello " + name