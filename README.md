# Prerequisites

In order to be executed, it is required `docker` and `python3` to be installed.

Also, [`conf.json`](https://github.com/CesareIurlaro/aws-proof-of-concept/blob/master/conf.json) file must be filled with the correct data. I already filled most of it with some default values (which
can be changed, if needed), the remaining `XXXXX` values must be compiled though.

- `TABLE_NAME`(i.e. the name of the table in which the script is going to write uploaded data)


- `POSTGRES_HOST` (i.e. the host where the Postgres DBMS is hosted)
- `POSTGRES_PORT` (i.e. the port on which the Postgres DBMS is exposing)
- `POSTGRES_DB` (i.e. the Postgres database on which the table `TABLE_NAME` is planned to be stored)
- `POSTGRES_USR` (i.e. the username allowed querying in Postgres)


- `AWS_ACCOUNT_ID` (i.e. the ID of the AWS account on which is hosted the Redshift Cluster)
- `AWS_REGION_NAME` (i.e. the region name in which the Redshift Cluster is hosted)

- `REDSHIFT_HOST` (i.e. the host where the Redshift Cluster is hosted, which is the JDBC URL in the cluster page,
  without the "jdbc:" at the beginning of the string and without the ":{port}/database" at the end of it)
- `REDSHIFT_PORT` (i.e. the port on which the Redshift Cluster is listening)
- `REDSHIFT_DB` (i.e. the Redshift database on which the table `TABLE_NAME` is planned to be stored)
- `REDSHIFT_USR` (i.e. the username allowed querying in Redshift)


- `BUCKET` (i.e. the bucket on which to store the content of the data queried by PostgreSQL)
- `SINK_FILE` (i.e. the name of the file written localy and uploaded in the bucket)


- `S3_FULL_ACCESS_ROLE` (i.e. the name of the role allowed with the full rights on the S3 bucket)
- `REDSHIFT_READ_S3_ROLE` (i.e. the name of the role which allows Redshift to read on the S3 bucket)

The following values correspond the `secrets` key, since they are sensible data.

- `AWS_ACCESS_KEY_ID` (i.e. the access key id of the IAM account responsible for the execution)
- `AWS_SECRET_KEY` (i.e. the secret access key id corresponding `AWS_ACCESS_KEY_ID`)
- `POSTGRES_PWD` (i.e. the password corresponding the `POSTGRES_USR` user)
- `REDSHIFT_PWD` (i.e. the password corresponding the `REDSHIFT_USR` user)

# Explanation

The scope of the program is to build and manage some docker containers. In particular, it:

1) Builds the two containers `ingestor` and `pg-to-aws` (which execution is respectively explained
   in [`ingestor/README.md`](https://github.com/CesareIurlaro/aws-proof-of-concept/tree/master/ingestor)
   and [`pg-to-aws/README.md`](https://github.com/CesareIurlaro/aws-proof-of-concept/tree/master/pg-to-aws).


2) Creates a container virtual network called `pg-net`.

3) Runs a `postgresql` container which is exposed in the `pg-net` as `pg-staging`

4) Sequentially runs the previously built containers, which during their executions will repeatedly communicate with the
   postgres container through the `pg-net`. They will both be removed right after their own execution.

5) Remove the `postgres` container and the `pg-net` container virtual network.

At the end of this, a `./data` folder will be created (if not already existing) on the host machine and also within it
there will be the `gzip` that `pg-to-aws` created, uploaded in the S3 bucket and imported into the Redshift table.

# Quick start

To make all of this happen, just run `start.sh`.
