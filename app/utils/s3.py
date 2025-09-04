from datetime import datetime
import logging
import boto3
from app.config import aws_settings

s3_client = boto3.client(
    "s3",
    aws_access_key_id=aws_settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=aws_settings.AWS_SECRET_ACCESS_KEY,
    region_name=aws_settings.AWS_REGION,
)

# To create the bucket if it does not exist, if exist Comment out.
#try:
#    s3_client.create_bucket(
#        Bucket=aws_settings.AWS_S3_BUCKET,
#        CreateBucketConfiguration={"LocationConstraint": aws_settings.AWS_REGION}
#    )
#    print(f"Bucket '{aws_settings.AWS_S3_BUCKET}' created.")
#except s3_client.exceptions.BucketAlreadyOwnedByYou:
#    print(f"Bucket '{aws_settings.AWS_S3_BUCKET}' already exists.")
#except Exception as e:
#    print(f"Error creating bucket: {e}")

def upload_file_to_s3(file_obj, filename, bucket=None):
    bucket = bucket or aws_settings.AWS_S3_BUCKET
    s3_client.upload_fileobj(file_obj, bucket, filename)

def download_file_from_s3(filename, bucket=None):
    bucket = bucket or aws_settings.AWS_S3_BUCKET
    file_obj = s3_client.get_object(Bucket=bucket, Key=filename)
    return file_obj['Body'].read()

def delete_file_from_s3(filename, bucket=None):
    bucket = bucket or aws_settings.AWS_S3_BUCKET
    s3_client.delete_object(Bucket=bucket, Key=filename)


def file_exists_in_s3(filename, bucket=None):
    bucket = bucket or aws_settings.AWS_S3_BUCKET
    try:
        s3_client.head_object(Bucket=bucket, Key=filename)
        return True
    except s3_client.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            return False
        logging.error(f"S3 error checking file '{filename}': {e}")
        raise
            