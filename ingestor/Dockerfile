FROM python:3.8.8
WORKDIR /code
RUN pip install --upgrade pip
RUN pip3 install sqlalchemy psycopg2 pandas numpy
COPY ingestor.py ingestor.py
COPY dbutils dbutils
COPY ddl ddl
CMD ["python", "-u", "ingestor.py"]