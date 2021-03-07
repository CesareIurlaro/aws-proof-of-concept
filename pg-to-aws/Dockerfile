FROM python:3.8.8
WORKDIR /code
RUN pip install --upgrade pip
RUN pip install sqlalchemy psycopg2 pandas numpy sqlalchemy-redshift boto3 pandas_redshift
COPY pg-to-aws.py pg-to-aws.py
COPY ddl ddl
COPY dbutils dbutils
CMD ["python", "-u", "pg-to-aws.py"]