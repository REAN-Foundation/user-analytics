import io
from typing import BinaryIO
from app.modules.storage.providers.awa_s3_storage_service import AwsS3StorageService
from app.modules.storage.providers.local_storage_service import LocalStorageService

###############################################################################

class StorageService:

    def __init__(self, provider: str = 'aws'):
        self.provider = provider
        if self.provider == 'aws':
            self.storage = AwsS3StorageService()
        else:
            self.storage = LocalStorageService()

    # For use cases where the file is already present locally or created locally
    async def upload_local_file(self, storage_location: str, local_file_path: str):
        return await self.storage.upload_local_file(storage_location, local_file_path)

    # Useful for the big files, streamed and multi-part data
    async def upload_file_as_stream(self, storage_location: str, stream: BinaryIO, file_name: str):
        return await self.storage.upload_file_as_stream(storage_location, stream, file_name)

    # Useful for the small files
    async def upload_file_as_object(self, storage_location: str, content, file_name: str):
        return await self.storage.upload_file_as_object(storage_location, content, file_name)

    # For use-cases where the file needs to be processed locally before passing it on in the response
    async def download_file_locally(self, storage_key: str, local_file_path: str):
        return await self.storage.download_file_locally(storage_key, local_file_path)

    # Useful for large files, streams and multi-part data
    async def download_file_as_stream(self, storage_key: str):
        return await self.storage.download_file_as_stream(storage_key)

    # Useful for small files
    async def download_file_as_object(self, storage_key: str) -> io.BytesIO:
        return await self.storage.download_file_as_object(storage_key)
