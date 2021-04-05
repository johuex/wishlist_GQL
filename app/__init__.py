import graphene
from fastapi import FastAPI, APIRouter, Request, Depends
# from fastapi.security import HTTPBasic

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
    router = APIRouter()
    app = FastAPI()
    #security = HTTPBasic()
    gql_app = GraphQLApp(
        schema=graphene.Schema(
            query=Query,
            mutation=Mutation),
        executor_class=AsyncioExecutor,
        graphiql=True
        )

    @router.api_route("/", methods=["GET", "POST"])
    @router.api_route("/gql", methods=["GET", "POST"])
    async def graphql(request: Request):
        return await gql_app.handle_graphql(request=request)

    app.include_router(router)
    #app.include_router(router, dependencies=[Depends(security)])

    return app


