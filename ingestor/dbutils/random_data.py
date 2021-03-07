import logging
import secrets
import string
import sys
from itertools import islice

import numpy as np
from setuptools.package_index import unique_everseen
import pandas as pd
from datetime import datetime

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="[%(asctime)s][INGESTOR][%(levelname)s] %(message)s")


def get_random_data_as_pandas(rows_cardinality):
    """
    Function that generates a random dataset which respects the TABLE definition exposed in the DDL_PATH.

    Strings in `id`, `title` and `description` are generated randomly but uniquely.
    Timestamps in `published_timestamp` are generated within a lower (my B-DAY <3) and an upper (execution-time) bounds.
    Timestamps in `last_update_timestamp` are generated adding a random time lapse (within 1 months and 3 years)
    to `published_timestamp`.

    Parameters:
         `rows_cardinality`: the number of rows that the generated dataset has to contain.
    """

    def generate_unique_random_strings(n, maxlength):
        """ Fast way to generate random strings: https://stackoverflow.com/a/48421303/3004162 """

        def gen_keys():
            def b36number(n, length, _range=range, _c=string.ascii_uppercase + string.digits):
                chars = [_c[0]] * length
                while n:
                    length -= 1
                    chars[length] = _c[n % 36]
                    n //= 36
                return ''.join(chars)

            limit = [None] * 12 + [36 ** l for l in range(12, maxlength)]
            while True:
                count = np.random.randint(12, maxlength)
                yield b36number(secrets.randbelow(limit[count]), count)

        return list(islice(unique_everseen(gen_keys()), n))

    try:
        lower_bound, upper_bound = datetime(year=1994, month=1, day=29).timestamp(), datetime.now().timestamp()
        published_unixtimes = np.random.randint(lower_bound, upper_bound, rows_cardinality)
        last_update_unixtimes = published_unixtimes + np.random.randint(2700000, 94650000, rows_cardinality)
        # 2700000 seconds ~= 1 month & 94650000 seconds ~= 3 years

        df = pd.DataFrame({
            "id": generate_unique_random_strings(rows_cardinality, 20),
            "title": generate_unique_random_strings(rows_cardinality, 20),
            "description": generate_unique_random_strings(rows_cardinality, 50),
            "published_timestamp": pd.to_datetime(published_unixtimes, unit='s'),
            "last_update_timestamp": pd.to_datetime(last_update_unixtimes, unit='s')})
        logging.info("A random dataset has correctly been generated.")
        return df
    except Exception as e:
        logging.error("An error occurred while generating a random dataset.")
        logging.error(e)
