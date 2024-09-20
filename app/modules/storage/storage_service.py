from app.modules.storage.providers.awa_s3_storage_service import AwsS3StorageService
from app.modules.storage.providers.local_storage_service import LocalStorageService

###############################################################################

class StorageService:

    def __init__(self, provider: str):
        self.provider = provider
        if self.provider == 'aws':
            self.storage = AwsS3StorageService()
        else:
            self.storage = LocalStorageService()

    async def upload_local_file(self, file_path: str):
        return await self.storage.upload_local_file(file_path)

    # Useful for the big files, streamed and multi-part data
    async def upload_file_as_stream_multipart(self, stream, file_name: str):
        return await self.storage.upload_file_as_stream_multipart(stream, file_name)

    # Useful for the small files
    async def upload_file_as_object(self, content, file_name: str):
        return await self.storage.upload_file_as_object(content, file_name)

    async def download_file_locally(self, storage_key: str, local_file_path: str):
        return await self.storage.download_file_locally(storage_key, local_file_path)

    # Useful for large files, streams and multi-part data
    async def download_file_as_stream_multipart(self, storage_key: str):
        return await self.storage.download_file_as_stream_multipart(storage_key)

    # Useful for small files
    async def download_file_as_object(self, content, file_name: str):
        return await self.storage.download_file_as_object(content, file_name)
