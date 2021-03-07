from . import *

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="[%(asctime)s][PG-TO-AWS][%(levelname)s] %(message)s")


def upload_file_to_bucket():
    """ Function that upload the file in the local DATA_PATH/SINK_FILE into the remote S3 bucket called BUCKET. """
    credentials = assume_role(S3_FULL_ACCESS_ROLE)
    try:
        session = boto3.session.Session(credentials["AccessKeyId"], credentials["SecretAccessKey"],
                                        credentials["SessionToken"], AWS_REGION_NAME)
        logging.info(f"Session correctly initialized with the {S3_FULL_ACCESS_ROLE} role.")
        try:
            s3_client = session.resource('s3')
            s3_client.meta.client.upload_file(Filename=f"{DATA_PATH / SINK_FILE}", Bucket=BUCKET, Key=SINK_FILE)
            logging.info(f"{SINK_FILE} correctly uploaded in the {BUCKET} bucket.")
        except Exception as e:
            logging.error(f"An error occurred while trying to upload {SINK_FILE} in the {BUCKET} bucket.")
            logging.error(e)
    except Exception as e:
        logging.error(f"An error occurred while trying to initialize a session with the {S3_FULL_ACCESS_ROLE} role.")
        logging.error(e)
