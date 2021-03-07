import logging
import sys

from dbutils.postgresql import get_table_as_pandas_batches
from dbutils.s3 import upload_file_to_bucket
from dbutils.redshift import upload_file_to_redshift

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="[%(asctime)s][PG-TO-AWS][%(levelname)s] %(message)s")
logging.info("Application started.")


get_table_as_pandas_batches()
upload_file_to_bucket()
upload_file_to_redshift()

logging.info(f"Container ended correctly.")
