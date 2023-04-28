import os
from typing import List

from google.cloud import storage


class GCSFileManager:
    def __init__(self, bucket_name, credentials_path=None):
        self.bucket_name = bucket_name
        self.client = self._get_storage_client(credentials_path)

    def _get_storage_client(self, credentials_path=None):
        if credentials_path:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
        return storage.Client()

    def create_file(self, file_path, remote_path):
        bucket = self.client.bucket(self.bucket_name)
        blob = bucket.blob(remote_path)
        blob.upload_from_filename(file_path)

    def read_file(self, remote_path):
        bucket = self.client.bucket(self.bucket_name)
        blob = bucket.blob(remote_path)
        return blob.download_as_string()

    def update_file(self, file_path, remote_path):
        bucket = self.client.bucket(self.bucket_name)
        blob = bucket.blob(remote_path)
        blob.upload_from_filename(file_path)

    def delete_file(self, remote_path):
        bucket = self.client.bucket(self.bucket_name)
        blob = bucket.blob(remote_path)
        blob.delete()

    def list_files(self, directory=None) -> List[str]:
        bucket = self.client.bucket(self.bucket_name)
        blobs = bucket.list_blobs(prefix=directory)
        return [blob.name for blob in blobs if not blob.name.endswith("/")]
