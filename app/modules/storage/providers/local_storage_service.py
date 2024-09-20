import os
from typing import AsyncIterable

###############################################################################

local_storage_path = os.getenv('LOCAL_STORAGE_PATH')

###############################################################################

class LocalStorageService:

    def __init__(self):
        pass

    async def upload_local_file(self, file_path: str):
        try:
            file_name = os.path.basename(file_path)
            local_file_path = os.path.join(local_storage_path, file_name)
            os.rename(file_path, local_file_path)
            print(f"File {file_path} uploaded to {local_file_path}")
            return True
        except FileNotFoundError:
            print("The file was not found")
            return False
        except Exception as e:
            print(f"Error in uploading file: {e}")
            return False

    async def upload_file_as_stream_multipart(self, stream: AsyncIterable[bytes], file_name: str):
        try:
            local_file_path = os.path.join(local_storage_path, file_name)
            async with open(local_file_path, 'wb') as file:
                async for chunk in stream:
                    file.write(chunk)
            print(f"File uploaded to {local_file_path}")
            return True
        except Exception as e:
            print(f"Error in uploading file: {e}")
            return False

    async def upload_file_as_object(self, content, file_name: str):
        try:
            local_file_path = os.path.join(local_storage_path, file_name)
            with open(local_file_path, 'wb') as file:
                file.write(content)
            print(f"File uploaded to {local_file_path}")
            return True
        except Exception as e:
            print(f"Error in uploading file: {e}")
            return False

    async def download_file_locally(self, storage_key: str, local_file_path: str):
        try:
            local_file_path = os.path.join(local_storage_path, local_file_path)
            with open(local_file_path, 'rb') as file:
                content = file.read()
            return content
        except FileNotFoundError:
            print("The file was not found")
            return None
        except Exception as e:
            print(f"Error in downloading file: {e}")
            return None

    async def download_file_as_stream_multipart(self, storage_key: str):
        try:
            local_file_path = os.path.join(local_storage_path, storage_key)
            async def stream_file() -> AsyncIterable[bytes]:
                with open(local_file_path, 'rb') as file:
                    while True:
                        chunk = file.read(1024)  # Read in chunks of 1024 bytes
                        if not chunk:
                            break
                        yield chunk
            file_content = stream_file()
            print(f"File {storage_key} downloaded as stream")
            return file_content
        except FileNotFoundError:
            print("The file was not found")
            return None
        except Exception as e:
            print(f"Error in downloading file: {e}")
            return None

    async def download_file_as_object(self, content, file_name: str):
        try:
            local_file_path = os.path.join(local_storage_path, file_name)
            with open(local_file_path, 'wb') as file:
                file.write(content)
            print(f"File downloaded to {local_file_path}")
            return True
        except Exception as e:
            print(f"Error in downloading file: {e}")
            return False

###############################################################################
