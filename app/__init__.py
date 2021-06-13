import graphene

from graphql.execution.executors.asyncio import AsyncioExecutor
from starlette.applications import Starlette
from starlette.graphql import GraphQLApp
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
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
    middleware = [Middleware(CORSMiddleware, allow_origins=['*'], allow_headers=['*'], allow_methods=['*'])]
    app = Starlette(routes=routes, middleware=middleware)
    return app


