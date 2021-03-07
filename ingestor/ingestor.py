import logging
import sys

from dbutils.postgresql import append_dataframe_to_postgres
from dbutils.random_data import get_random_data_as_pandas

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="[%(asctime)s][INGESTOR][%(levelname)s] %(message)s")
logging.info(f"Application started.")

random_data_df = get_random_data_as_pandas(rows_cardinality=5000000)
append_dataframe_to_postgres(random_data_df)

logging.info(f"Container ended correctly.")
