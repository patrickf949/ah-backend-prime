from concurrent.futures import ThreadPoolExecutor

import boto3
from django.conf import settings
from django.tasks import task
from django.tasks.base import TaskResult, TaskResultStatus
from django.tasks.backends.immediate import ImmediateBackend
from django.utils.crypto import get_random_string


class ThreadPoolTaskBackend(ImmediateBackend):
    """
    Lightweight in-process task backend for Django 6.0 `django.tasks`.
    Executes tasks asynchronously in a background ThreadPoolExecutor so
    HTTP responses return immediately without requiring Celery or Redis.
    """

    def __init__(self, alias, params):
        super().__init__(alias, params)
        max_workers = self.options.get("MAX_WORKERS", 2)
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def enqueue(self, task_obj, args, kwargs):
        self.validate_task(task_obj)
        task_result = TaskResult(
            task=task_obj,
            id=get_random_string(32),
            status=TaskResultStatus.READY,
            enqueued_at=None,
            started_at=None,
            last_attempted_at=None,
            finished_at=None,
            args=args,
            kwargs=kwargs,
            backend=self.alias,
            errors=[],
            worker_ids=[],
        )
        self.executor.submit(self._execute_task, task_result)
        return task_result


@task
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
