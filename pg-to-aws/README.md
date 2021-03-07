## PG-TO-AWS MODULE

The [`pg-to-aws.py`](https://github.com/CesareIurlaro/aws-proof-of-concept/blob/master/pg-to-aws/pg-to-aws.py) module
execution, for sake of decoupling, is separated by the ingestor one.

It is responsible to upload to S3 a CSV compressed file containing the data previously written into PostgreSQL by
the [`ingestor.py`](https://github.com/CesareIurlaro/aws-proof-of-concept/blob/master/ingestor/ingestor.py) module.

It does so in the following steps:

1) It queries the PotsgreSQL for the data by chunks
2) While it keep querying, it also writes a CSV compressed file with the already queried content (memory-optimization)
3) It uploads the final CSV into a specified S3 bucket
4) It imports the data from the S3 to a Redshift Table

Notice that in order to perform well it has been used the condition of the B-TREE index previously created by the
[`ingestor.py`](https://github.com/CesareIurlaro/aws-proof-of-concept/blob/master/ingestor/ingestor.py) module as well
as the `COPY` Redshift-specific instruction.

Once more it is worth saying that this could have been done in a more generic and direct way within `Spark`.

## Cloud Configuration

The [`pg-to-aws.py`](https://github.com/CesareIurlaro/aws-proof-of-concept/blob/master/pg-to-aws/pg-to-aws.py) module
execution depends on a correct AWS environment setup, on which there must have been created the correct IAM user, roles,
policies, cluster, vpn, etc. In order to be sure this is done, follow the instruction written in
the [`pg-to-aws/AWS-ENV-SETUP-GUIDE.md`](https://github.com/CesareIurlaro/aws-proof-of-concept/blob/master/pg-to-aws/AWS-ENV-SETUP-GUIDE.md)
.

### TODO:

This process may be programmatically done throught the
library [`troposphere`](https://github.com/cloudtools/troposphere) and the AWS CloudFormation service.

This will allow to avoid the manual configuration.
