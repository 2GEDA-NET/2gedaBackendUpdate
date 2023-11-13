import boto3
from botocore.exceptions import NoCredentialsError
from django.core.files.base import ContentFile
from decouple import config

# Load your S3 configuration
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME')


s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_S3_REGION_NAME
)


def upload_file_to_s3(file_path, s3_key):
    try:
        s3.upload_file(file_path, AWS_STORAGE_BUCKET_NAME, s3_key)
        return True
    except NoCredentialsError:
        print("AWS credentials not available")
        return False

# Retrieve a file from S3
def get_file_from_s3(s3_key, local_path):
    try:
        s3.download_file(AWS_STORAGE_BUCKET_NAME, s3_key, local_path)
        return True
    except NoCredentialsError:
        print("AWS credentials not available")
        return False

# Example usage
# file_to_upload = 'path/to/local/file.txt'
# s3_key = 'folder/filename.txt'

# if upload_file_to_s3(file_to_upload, s3_key):
#     print(f"File {file_to_upload} uploaded to S3 with key {s3_key}")

# local_download_path = 'path/to/local/downloaded_file.txt'
# if get_file_from_s3(s3_key, local_download_path):
#     print(f"File downloaded from S3 with key {s3_key} to {local_download_path}")
