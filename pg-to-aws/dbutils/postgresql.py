import logging
import os
import sys

from . import POSTGRES_ENGINE, DATA_PATH, TABLE_NAME, SINK_FILE
import numpy as np
import pandas as pd

INDEX_HINT = "CAST(DATE_PART('year', DATE(published_timestamp)) AS INT)"
DB_PARALLELIZATION = 5  # MUST BE > 2

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="[%(asctime)s][PG-TO-AWS][%(levelname)s] %(message)s")
logging.info(f"Actual parallelization level is: {DB_PARALLELIZATION}.")


def get_table_as_pandas_batches(buffer_size=2):
    """ Function that reads the TABLE_NAME PostgreSQL `TABLE` table exploiting the INDEX_HINT B-TREE index and appends
        its content by chunks into `SINK_FILE`, which is a CSV file compressed with GZIP.
    """

    sql = f"SELECT MIN({INDEX_HINT}), MAX({INDEX_HINT}) FROM {TABLE_NAME}"
    lower_date, upper_date = POSTGRES_ENGINE.connect().execute(sql).fetchone()
    boundaries = np.linspace(lower_date, upper_date, DB_PARALLELIZATION, dtype=int)

    def get_bounded_df(lower_bound, upper_bound):
        """ Support function that returns data included in the [`lower_bound`, `upper_bound`) range of TABLE_NAME table
            in form of pandas DataFrame.
        """
        return pd.read_sql(f"SELECT * FROM {TABLE_NAME} "
                           f"WHERE {INDEX_HINT} >= {lower_bound} AND {INDEX_HINT} < {upper_bound}", POSTGRES_ENGINE)

    try:
        buffer = []
        for i, _ in enumerate(boundaries[:-1]):
            if (i % buffer_size) == 0 and i > 0:
                write_pandas_batches_as_csv(buffer)
                buffer = []
            buffer += [get_bounded_df(boundaries[i], boundaries[i + 1])]

        buffer += [pd.read_sql(f"SELECT * FROM {TABLE_NAME} WHERE {INDEX_HINT} = {boundaries[-1]}", POSTGRES_ENGINE)]
        write_pandas_batches_as_csv(buffer)

        logging.info("Data correctly wrote into CSV in chunks.")
    except Exception as e:
        logging.error("An error occurred while loading in memory or writing the data batches. """)
        logging.error(e)


def write_pandas_batches_as_csv(pandas_batches, output_path=DATA_PATH / SINK_FILE):
    """ Support function that writes the `pandas_batches` content into the `output_path` in form of GZIP CSV.

        Parameters:
            `pandas_batches`: list of pandas DataFrame
    """

    for i, df in enumerate(pandas_batches):
        df.to_csv(output_path, mode='a+', header=(not os.path.exists(output_path)), index=False, compression="gzip")
        logging.info(f"Chunk #{i + 1} written.")
    logging.info(f"Group of chunks successfully written.")
