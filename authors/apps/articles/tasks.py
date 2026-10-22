import boto3
from celery import shared_task
from django.conf import settings

@shared_task
def delete_s3_image(key):
    """
    Background task to delete an image from S3/R2 given its key.
    """
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        region_name=settings.AWS_S3_REGION_NAME,
        config=boto3.session.Config(signature_version='s3v4')
    )

    try:
        s3_client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key)
        print(f"Successfully deleted {key} from S3")
    except Exception as e:
        print(f"Failed to delete {key} from S3: {e}")
