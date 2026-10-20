from unittest.mock import patch


class ExternalServicesMockMixin:
    """
    Mocks the external services touched by the article views so tests
    never need a running Redis instance, Celery worker or Cloudflare R2.

    Exposes the mocks as attributes for assertions:
        self.mock_cache   -> django cache used for autosave drafts
        self.mock_boto3   -> boto3 module used for R2 presigned urls
        self.mock_delete_image_task -> celery task for R2 image deletion
    """

    def setUp(self):
        super().setUp()
        self.mock_cache = self._start_patch('authors.apps.articles.views.cache')
        self.mock_boto3 = self._start_patch('authors.apps.articles.views.boto3')
        self.mock_delete_image_task = self._start_patch(
            'authors.apps.articles.tasks.delete_s3_image')

    def _start_patch(self, target):
        patcher = patch(target)
        mocked = patcher.start()
        self.addCleanup(patcher.stop)
        return mocked
