## INGESTOR MODULE

The [`ingestor.py`](https://github.com/CesareIurlaro/aws-proof-of-concept/blob/master/ingestor/ingestor.py) module does the following:

1) It generates 5 milions rows of random - but compliant with a specific DDL schema - data using
   the `get_random_data_as_pandas` function, in form of `pandas` `DataFrame`.


2) It writes the data generated in the step-1 into a table in a PostgreSQL DBMS through the `append_dataframe_to_postgres`
   function. Before trying to append the data, the script executes the DDL file containing the DDL definitions.

---

It is worth noticing a couple of points:

1) A **B-Tree index** is defined in the DDL file. It will improve performance on read operations which filters use
   ranges on the timestamp columns.


2) The writing part are made with the PostgreSQL specific query since this is a simple use case in which we are making
   some assumptions like that the system is:

    - not distributed
    - invariable

   \
   In a more realistic production-like context in which a single writing point could be a breaking-point/bottleneck or
   in which there is no guarantee that the DBMS will ever stay the same (updates and migrations to NoSQL are, for
   example, a common outcome) a more robust and reliable approach would be high suggested.

   \
   `Spark` for example, is a framework which would offer a solution to both problems, since it guarantees that the same
   behaviour can be achieved independently by the underlying storage solution with the same code - which is not the case
   for any not-standard SQL syntax as the `COPY` used by the `append_dataframe_to_postgres` in order to optimize.
   
