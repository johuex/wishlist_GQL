import logging
import boto3
from botocore.exceptions import ClientError


def upload_file(file, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_fileobj(file, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def download_file(bucket_name, object_name, expiration=3600):
    """Generate a presigned and temporary URL to share an S3 object

        :param bucket_name: string
        :param object_name: string
        :param expiration: Time in seconds for the presigned URL to remain valid
        :return: Presigned URL as string. If error, returns None.
        """

    # Generate a presigned URL for the S3 object
    s3_client = boto3.client('s3')

    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response


def delete_file(bucket, file_name):
    s3 = boto3.client('s3')
    try:
        s3.Object(bucket, file_name).delete()
    except ClientError as e:
        logging.error(e)
        return False
    return True


def check_format(file_name):
    """Check for uploading only pictures"""
    formats = ['.png', '.jpg', '.bmp']
    if any(f in file_name for f in formats):
        return True
    else:
        return False
