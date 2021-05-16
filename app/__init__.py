import graphene
#from fastapi import FastAPI, APIRouter, Request

from graphql.execution.executors.asyncio import AsyncioExecutor
from starlette.applications import Starlette
from starlette.graphql import GraphQLApp
from starlette.routing import Route

from app.queries import Query
from app.mutations import Mutation
from .database import SessionLocal, engine
from .models import Base
from .auth import AuthHandler


def create_app():
    routes = [
        Route('/', GraphQLApp(schema=graphene.Schema(
                              query=Query,
                              mutation=Mutation),
                              executor_class=AsyncioExecutor,
                              graphiql=True,))
    ]

    app = Starlette(routes=routes)
    return app
'''
    router = APIRouter()
    app = FastAPI()
    gql_app = GraphQLApp(
        schema=graphene.Schema(
            query=Query,
            mutation=Mutation),
        executor_class=AsyncioExecutor,
        graphiql=True,
        )

    @router.api_route("/", methods=["GET", "POST"])
    @router.api_route("/gql", methods=["GET", "POST"])
    async def graphql(request: Request):
        return await gql_app.handle_graphql(request=request)

    app.include_router(router)

    return app'''


