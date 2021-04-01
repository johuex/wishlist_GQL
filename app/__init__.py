import graphene
from fastapi import FastAPI
from graphql.execution.executors.asyncio import AsyncioExecutor
from starlette.graphql import GraphQLApp
from app.queries import Query
from app.mutation import Mutation
# from app.types import Types
from .database import SessionLocal, engine, db
from .models import Base

dab = SessionLocal()

models.Base.metadata.create_all(bind=engine)


def create_app():
    app = FastAPI()
    app.add_route(
        "/graphql",
        GraphQLApp(
            schema=graphene.Schema(query=Query, mutation=Mutation),
            executor_class=AsyncioExecutor, graphiql=True
        )
    )
    return app


