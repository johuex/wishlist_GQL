import uvicorn
from app import create_app

app = create_app()


#uvicorn.run(app, '0.0.0.0', '8000')
