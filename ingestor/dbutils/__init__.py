import json
import os
import sys
from pathlib import Path

from sqlalchemy import create_engine
import logging

path = str(Path("conf.json").absolute())
with open(path) as f:
    conf = json.load(f)
secrets = conf["secrets"]

conn = "postgresql"
postgres_usr = conf['POSTGRES_USR']
postgres_pwd = secrets['POSTGRES_PWD']
postgres_host = conf['POSTGRES_HOST']
postgres_port = conf['POSTGRES_PORT']
postgres_db = conf['POSTGRES_DB']

POSTGRES_ENGINE = create_engine(f"{conn}://{postgres_usr}:{postgres_pwd}@{postgres_host}:{postgres_port}/{postgres_db}")
TABLE_NAME = conf["TABLE_NAME"]

DDL_PATH = "ddl/create_fixtures.sql"

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="[%(asctime)s][INGESTOR][%(levelname)s] %(message)s")
logging.info("Environment variables correctly initiated.")
