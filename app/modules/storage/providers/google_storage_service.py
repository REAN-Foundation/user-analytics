import io
import os
from typing import AsyncIterable, BinaryIO
from google.cloud import storage
from app.common.utils import print_exception

###############################################################################
# Set up authentication by setting the GOOGLE_APPLICATION_CREDENTIALS
# environment variable to the path of your service account key file,
# or use from_service_account_json() method.

#bucket_name = os.getenv('GCP_BUCKET')
bucket_name = 'user-analytics-storage'

###############################################################################

class AwsS3StorageService:

    def __init__(self):
        self.client = storage.Client()
        self.bucket = self.client.get_bucket(bucket_name)

    async def upload_local_file(self, storage_location: str, local_file_path: str):
        try:
            if not os.path.exists(local_file_path):
                print(f"File '{local_file_path}' does not exist")
                return False

            file_name = os.path.basename(local_file_path)
            storage_key = f"{storage_location}/{file_name}"
            blob = self.bucket.blob(storage_key)
            blob.upload_from_filename(local_file_path)

            print(f"File '{local_file_path}' uploaded to '{bucket_name}/{storage_key}'")
            return True
        except Exception as e:
            print_exception(e)
            return False

    async def upload_file_as_stream(self, storage_location: str, stream: BinaryIO, file_name: str):
        try:
            storage_key = f"{storage_location}/{file_name}"
            assert hasattr(stream, 'read') and hasattr(stream, 'seek'), "Stream must be a file-like object with read and seek methods"
            blob = self.bucket.blob(storage_key)
            stream.seek(0)
            blob.upload_from_file(stream)
            print(f"File uploaded successfully to {bucket_name}/{file_name}")
            return True
        except Exception as e:
            print(f"Error in uploading file: {e}")
            return False

    async def upload_file_as_object(self, storage_location: str, content, file_name: str):
        try:
            storage_key = f"{storage_location}/{file_name}"
            buffer: io.BytesIO = io.BytesIO(content)
            buffer.seek(0)
            blob = self.bucket.blob(storage_key)
            blob.upload_from_file(content)
            print(f"File uploaded to {bucket_name}/{file_name}")
            return True
        except Exception as e:
            print_exception(e)
            return False

    async def download_file_locally(self, storage_key: str, local_file_path: str):
        try:
            # Make sure the file path directory exists
            os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

            blob = self.bucket.blob(storage_key)
            with open(local_file_path, "wb") as file:
                blob.download_to_file(file)

            # Or altenatively
            # blob.download_to_filename(local_file_path)

            print(f"File downloaded from {bucket_name}/{storage_key} to {local_file_path}")

            return True
        except Exception as e:
            print_exception(e)
            return False

    async def download_file_as_stream(self, storage_key: str) -> AsyncIterable[bytes]:
        try:
            blob = self.bucket.blob(storage_key)
            stream = io.BytesIO()
            blob.download_to_file(stream)
            stream.seek(0)
            print(f"File {storage_key} downloaded from {bucket_name} as stream")
            return stream
        except Exception as e:
            print_exception(e)
            return None

    async def download_file_as_object(self, storage_key: str) -> io.BytesIO:
        try:
            blob = self.bucket.blob(storage_key)
            buffer = io.BytesIO()
            blob.download_to_file(buffer)
            buffer.seek(0)
            print(f"File {storage_key} downloaded from {bucket_name} as object")
            return buffer
        except Exception as e:
            print_exception(e)
            return None
