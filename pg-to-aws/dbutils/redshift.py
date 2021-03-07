from . import *

import pandas_redshift as pr

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="[%(asctime)s][PG-TO-AWS][%(levelname)s] %(message)s")


def create_redshift_entities_if_absent():
    """
    A function used to be sure that the structures defined in the DDL file addressed by DDL_PATH exist.
    If they don't exist, they are created. If they already exist, nothing more happens.
    """
    try:
        with open(f"{DDL_PATH}") as file:
            sql = ''.join(file.readlines())
            sql = sql.replace("${TABLE_NAME}", TABLE_NAME)
            pr.connect_to_redshift(REDSHIFT_DB, REDSHIFT_HOST, REDSHIFT_USR, REDSHIFT_PORT, password=REDSHIFT_PWD)
            pr.exec_commit(sql)
        logging.info("Fixtures needed are online.")
    except Exception as e:
        logging.error("An error raised during the creation of the fixtures:")
        logging.error(e)


def upload_file_to_redshift():
    """
    A function that append the 's3://BUCKET/SINK_FILE' located file content into the `TABLE_NAME` Redshift table.

    """
    create_redshift_entities_if_absent()

    sql = f"""
        COPY {TABLE_NAME} FROM 's3://{BUCKET}/{SINK_FILE}'
        CREDENTIALS 'aws_iam_role={get_arn_from_role(REDSHIFT_READ_S3_ROLE)}'
        GZIP CSV IGNOREHEADER 1
   """
    try:
        pr.connect_to_redshift(REDSHIFT_DB, REDSHIFT_HOST, REDSHIFT_USR, REDSHIFT_PORT, password=REDSHIFT_PWD)
        pr.exec_commit(sql)
        logging.info(f"{BUCKET}/{SINK_FILE} correctly imported into Redshift's `{TABLE_NAME}` table")
    except Exception as e:
        logging.error(f"An error occurred while trying to import "
                      f"{BUCKET}/{SINK_FILE} into Redshift's `{TABLE_NAME}` table")
        logging.error(e)
