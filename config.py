from sqlalchemy import create_engine
import os

MAX_BLOCKS_TO_FETCH = 100
CONFIG_FOLDER = 'config/'

def init_heroku(live=False):
    if live:
        HEROKU_DB_URL = os.environ.get("HEROKU_POSTGRESQL_BLUE_URL")
    else:
        with open(CONFIG_FOLDER + "database_url", "r") as file:
            HEROKU_DB_URL = file.read().strip()
    
    heroku_engine = create_engine(HEROKU_DB_URL.replace("+asyncpg",""))
    conn = heroku_engine.connect()
    return conn

