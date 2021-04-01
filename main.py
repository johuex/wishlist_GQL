import uvicorn
from app import create_app
from app.database import db

app = create_app()

@app.on_event("startup")
async def startup():
    await db.connect()


@app.on_event("shutdown")
async def shutdown():
    await db.disconnect()


uvicorn.run(app,)
