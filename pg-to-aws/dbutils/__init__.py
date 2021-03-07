import json
import logging
import os
import sys
from pathlib import Path

import boto3
from sqlalchemy import create_engine

conf = json.load(open('conf.json'))
secrets = conf["secrets"]

conn = "postgresql"
postgres_usr = conf['POSTGRES_USR']
postgres_pwd = secrets['POSTGRES_PWD']
postgres_host = conf['POSTGRES_HOST']
postgres_port = conf['POSTGRES_PORT']
postgres_db = conf['POSTGRES_DB']

POSTGRES_ENGINE = create_engine(f"{conn}://{postgres_usr}:{postgres_pwd}@{postgres_host}:{postgres_port}/{postgres_db}")

DATA_PATH = Path("data")
if not os.path.exists(DATA_PATH):
    os.mkdir(DATA_PATH)

DDL_PATH = "ddl/create_fixtures.sql"

AWS_ACCOUNT_ID = conf["AWS_ACCOUNT_ID"]
AWS_ACCESS_KEY_ID = secrets["AWS_ACCESS_KEY_ID"]
AWS_SECRET_KEY = secrets["AWS_SECRET_KEY"]
AWS_REGION_NAME = conf["AWS_REGION_NAME"]

TABLE_NAME = conf["TABLE_NAME"]
REDSHIFT_HOST = conf["REDSHIFT_HOST"]
REDSHIFT_PORT = conf["REDSHIFT_PORT"]
REDSHIFT_DB = conf["REDSHIFT_DB"]
REDSHIFT_USR = conf["REDSHIFT_USR"]
REDSHIFT_PWD = secrets["REDSHIFT_PWD"]

BUCKET = conf["BUCKET"]
SINK_FILE = conf["SINK_FILE"]

S3_FULL_ACCESS_ROLE = conf["S3_FULL_ACCESS_ROLE"]
REDSHIFT_READ_S3_ROLE = conf["REDSHIFT_READ_S3_ROLE"]

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="[%(asctime)s][PG-TO-AWS][%(levelname)s] %(message)s")
logging.info("Environment variables correctly initiated.")


def get_arn_from_role(role):
    """ Support function that, given a `role`, returns its arn identifier. """
    return f"arn:aws:iam::{AWS_ACCOUNT_ID}:role/{role}"


def assume_role(role):
    """  Function that, given a `role`, let the program to assume it in order to temporarily extend its permissions. """
    try:
        sts_client = boto3.client('sts', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_KEY)
        credentials = sts_client.assume_role(RoleArn=get_arn_from_role(role), RoleSessionName=f"{role}SessionName")
        logging.info(f"Program is assuming the {role} role.")
        return credentials["Credentials"]
    except Exception as e:
        logging.error(f"An error occurred while trying to assume the {role} role.")
        logging.error(e)
