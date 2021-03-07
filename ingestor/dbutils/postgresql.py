import csv
import logging
import sys

from . import POSTGRES_ENGINE, DDL_PATH, TABLE_NAME
import io

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="[%(asctime)s][INGESTOR][%(levelname)s] %(message)s")


def append_dataframe_to_postgres(df):
    """
    A function that append the `df` pandas DataFrame content into the PostgreSQL `TABLE_NAME` table,
    whether it already exists or not.
    """

    def create_postgres_entities_if_absent():
        """
        A function used to be sure that the structures defined in the DDL file addressed by DDL_PATH exist.
        If they don't exist, they are created. If they already exist, nothing more happens.
        Notice that along the structures there's also an index, which strongly improves reading performance in
        our specific use case.
        """
        try:
            with open(f"{DDL_PATH}") as file:
                sql = ''.join(file.readlines())
                sql = sql.replace("${TABLE_NAME}", TABLE_NAME)
                POSTGRES_ENGINE.execute(sql)
            logging.info("Fixtures needed are online.")
        except Exception as e:
            logging.error("An error raised during the creation of the fixtures:")
            logging.error(e)

    def psql_insert_copy(table, conn, keys, data_iter):
        """ https://stackoverflow.com/a/55495065/3004162
        Optimized way to write data in PostgreSQL using the most efficient batch-writing native command `COPY`.

        The `COPY` command requires data to be written in the CSV format. This function writes the source dataframe in
        CSV format, but also keeps it in-memory so to allow a computation that avoid unneeded intermediate writing steps.
        In order to avoid memory bottleneck, this procedure is done by batch (which size is defined by chunksize).
        The bigger the batch size, the bigger the memory occupied, but also the faster the writing procedure.
        """
        try:
            dbapi_conn = conn.connection
            with dbapi_conn.cursor() as cursor:
                buffer = io.StringIO()
                writer = csv.writer(buffer)
                writer.writerows(data_iter)
                buffer.seek(0)

                columns = ', '.join(f'"{k}"' for k in keys)
                table_name = f'{table.schema}.{table.name}' if table.schema else table.name

                sql = f'COPY {table_name} ({columns}) FROM STDIN WITH CSV'
                cursor.copy_expert(sql=sql, file=buffer)
            logging.info("In-memory data batch correctly wrote in PostgreSQL.")
        except Exception as e:
            logging.error("An error raised trying to write an in-memory data batch in PostgresSQL:")
            logging.error(e)

    logging.info("Initiating the writing process in PostgreSQL.")
    create_postgres_entities_if_absent()

    try:
        df.to_sql(TABLE_NAME, POSTGRES_ENGINE,
                  method=psql_insert_copy, if_exists="append", index=False, chunksize=25000)
        logging.info("The total amount of data has been correctly wrote in PostgreSQL.")
    except Exception as e:
        logging.error("An error raised during the writing process in PostgresSQL:")
        logging.error(e)
