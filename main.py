import uvicorn
from app import create_app

uvicorn.run(create_app())
