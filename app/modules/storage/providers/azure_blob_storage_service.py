from io import BytesIO
import os
import shutil
from typing import AsyncIterable, BinaryIO

from app.common.utils import print_exception
from azure.storage.blob import BlobServiceClient

###############################################################################

azure_connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
blob_container_name = os.getenv('AZURE_CONTAINER_NAME')

###############################################################################

class AzureBlobStorageService:

    def __init__(self):
        self.service = BlobServiceClient.from_connection_string(azure_connection_string)
        self.container_client = self.service.get_container_client(blob_container_name)

    async def upload_local_file(self, storage_location: str, local_file_path: str):
        try:
            if not os.path.exists(local_file_path):
                print(f"File '{local_file_path}' does not exist")
                return False

            file_name = os.path.basename(local_file_path)
            storage_key = f"{storage_location}/{file_name}"
            with open(local_file_path, 'rb') as f:
                self.container_client.upload_blob(name=storage_key, data=f, overwrite=True)
            print(f"File '{local_file_path}' uploaded to '{blob_container_name}/{storage_key}'")
            return True
        except Exception as e:
            print_exception(e)
            return False

    async def upload_file_as_stream(self, storage_location: str, stream: BinaryIO, file_name: str):
        try:
            storage_key = f"{storage_location}/{file_name}"
            assert hasattr(stream, 'read') and hasattr(stream, 'seek'), "Stream must be a file-like object with read and seek methods"
            stream.seek(0)
            self.container_client.upload_blob(name=storage_key, data=stream, overwrite=True)
            print(f"File uploaded successfully to {blob_container_name}/{storage_key}")
            return True
        except Exception as e:
            print(f"Error in uploading file: {e}")
            return False

    async def upload_file_as_object(self, storage_location: str, content, file_name: str):
        try:
            storage_key = f"{storage_location}/{file_name}"
            buffer: BytesIO = BytesIO(content)
            buffer.seek(0)
            self.container_client.upload_blob(name=storage_key, data=buffer, overwrite=True)
            print(f"File uploaded to {blob_container_name}/{file_name}")
            return True
        except Exception as e:
            print_exception(e)
            return False

    async def download_file_locally(self, storage_key: str, local_file_path: str):
        try:
            with open(local_file_path, "wb") as file:
                file.write(self.container_client.download_blob(storage_key).readall())
            print(f"File downloaded from {blob_container_name}/{storage_key} to {local_file_path}")
            return True
        except Exception as e:
            print_exception(e)
            return False

    async def download_file_as_stream(self, storage_key: str):
        try:
            return self.container_client.download_blob(storage_key).readall()
        except Exception as e:
            print_exception(e)
            return None

    async def download_file_as_object(self, storage_key: str) -> BytesIO:
        try:
            buffer = BytesIO()
            buffer.write(self.container_client.download_blob(storage_key).readall())
            buffer.seek(0)
            print(f"File {storage_key} downloaded from {blob_container_name} as object")
            return buffer
        except Exception as e:
            print_exception(e)
            return None
