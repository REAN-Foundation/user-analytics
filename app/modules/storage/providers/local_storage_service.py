from io import BytesIO
import os
import shutil
from typing import AsyncIterable, BinaryIO

from app.common.utils import print_exception

###############################################################################

local_storage_path = os.getenv('LOCAL_STORAGE_PATH')

###############################################################################

class LocalStorageService:

    def __init__(self):
        pass

    async def upload_local_file(self, storage_location: str, local_file_path: str):
        try:
            if not os.path.exists(local_file_path):
                print(f"File '{local_file_path}' does not exist")
                return False

            file_name = os.path.basename(local_file_path)
            storage_path = f"{local_storage_path}/{storage_location}"
            os.makedirs(os.path.dirname(storage_path), exist_ok=True)
            destination_path = f"{storage_path}/{file_name}"

            shutil.copy(local_file_path, destination_path)

            print(f"File '{local_file_path}' uploaded to '{storage_path}'")
            return True
        except Exception as e:
            print_exception(e)
            return False

    async def upload_file_as_stream(self, storage_location: str, stream: BinaryIO, file_name: str):
        try:
            storage_path = f"{local_storage_path}/{storage_location}"
            os.makedirs(os.path.dirname(storage_path), exist_ok=True)
            destination_path = f"{storage_path}/{file_name}"
            stream.seek(0)
            with open(destination_path, 'wb') as f:
                shutil.copyfileobj(stream, f)
            print(f"File uploaded successfully to {destination_path}")
            return True
        except Exception as e:
            print(f"Error in uploading file: {e}")
            return False

    async def upload_file_as_object(self, storage_location: str, content, file_name: str):
        try:
            storage_path = f"{local_storage_path}/{storage_location}"
            os.makedirs(os.path.dirname(storage_path), exist_ok=True)
            destination_path = f"{storage_path}/{file_name}"
            with open(destination_path, 'wb') as f:
                f.write(content)
            print(f"File uploaded to {destination_path}")
            return True
        except Exception as e:
            print_exception(e)
            return False

    async def download_file_locally(self, storage_key: str, local_file_path: str):
        try:
            storage_path = f"{local_storage_path}/{storage_key}"
            if not os.path.exists(storage_path):
                print(f"File with storage key '{storage_key}' does not exist")
                return False

            os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
            shutil.copy(storage_path, local_file_path)

            print(f"File downloaded from {storage_path} to {local_file_path}")
            return True
        except Exception as e:
            print_exception(e)
            return False

    async def download_file_as_stream(self, storage_key: str):
        try:
            storage_path = f"{local_storage_path}/{storage_key}"
            if not os.path.exists(storage_path):
                print(f"File with storage key '{storage_key}' does not exist")
                return None

            return open(storage_path, 'rb')
        except Exception as e:
            print_exception(e)
            return None

    async def download_file_as_object(self, storage_key: str) -> BytesIO:
        try:
            storage_path = f"{local_storage_path}/{storage_key}"
            if not os.path.exists(storage_path):
                print(f"File with storage key '{storage_key}' does not exist")
                return None
            buffer = BytesIO()
            with open(storage_path, 'rb') as f:
                buffer.write(f.read())
            buffer.seek(0)
            print(f"File {storage_key} downloaded from {storage_path} as object")
            return buffer
        except Exception as e:
            print_exception(e)
            return None
