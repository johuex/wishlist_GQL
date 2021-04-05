import os
from dotenv import load_dotenv


dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


class Config(object):
    SQLALCHEMY_DATABASE_URL = os.environ.get('DATABASE_URL')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    # SQLALCHEMY_DATABASE_URL = "postgresql://wlist:@wlist.cfh2do2onn3t.eu-central-1.rds.amazonaws.com/wlist"