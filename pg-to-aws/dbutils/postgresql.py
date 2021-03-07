import logging
import os
import sys

from . import POSTGRES_ENGINE, DATA_PATH, TABLE_NAME, SINK_FILE
import numpy as np
import pandas as pd

INDEX_HINT = "CAST(DATE_PART('year', DATE(published_timestamp)) AS INT)"
DB_PARALLELIZATION = 5

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="[%(asctime)s][PG-TO-AWS][%(levelname)s] %(message)s")
logging.info(f"Actual parallelization level is: {DB_PARALLELIZATION}.")


def get_table_as_pandas_batches():
    """ Function that reads the TABLE_NAME PostgreSQL `TABLE` table exploiting the INDEX_HINT B-TREE index.

        Returns a list of pandas DataFrame, each of them is a ranged batch of `TABLE`.
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
        batches = ([get_bounded_df(boundaries[i], boundaries[i + 1]) for i, _ in enumerate(boundaries[:-1])] +
                   [pd.read_sql(f"SELECT * FROM {TABLE_NAME} WHERE {INDEX_HINT} = {boundaries[-1]}", POSTGRES_ENGINE)])
        logging.info("Data correctly loaded in batches.")
        return batches
    except Exception as e:
        logging.error("An error occurred while loading in memory the data batches. """)
        logging.error(e)


def write_pandas_batches_as_csv(pandas_batches, output_path=DATA_PATH / SINK_FILE):
    """ Function that writes the `pandas_batches` content into the `output_path` in form of GZIP CSV.

        Parameters:
            `pandas_batches`: list of pandas DataFrame
    """

    if os.path.exists(output_path):
        logging.info("File already exists. None action taken.")
    else:
        for i, df in enumerate(pandas_batches):
            df.to_csv(output_path, mode='a+', header=(i == 0), index=False, compression="gzip")
            logging.info(f"Chunk #{i + 1} written.")
