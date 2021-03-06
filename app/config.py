import os
from dotenv import load_dotenv


dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


class Config(object):
    SQLALCHEMY_DATABASE_URL = os.environ.get('DATABASE_URL')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    bucket = os.environ.get('bucket')
    EMAIL_HOST = os.environ.get('EMAIL_HOST')
    EMAIL_PORT = os.environ.get('EMAIL_PORT')
    EMAIL_LOGIN = os.environ.get('EMAIL_LOGIN')
    EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
