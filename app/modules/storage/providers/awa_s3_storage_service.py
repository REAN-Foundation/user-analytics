import io
import os
from typing import AsyncIterable, BinaryIO
import boto3
from app.common.utils import print_exception

###############################################################################

aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
region_name = os.getenv('AWS_REGION')
bucket_name = os.getenv('AWS_BUCKET')

###############################################################################

class AwsS3StorageService:

    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )

    async def upload_local_file(self, storage_location: str, local_file_path: str):
        try:
            if not os.path.exists(local_file_path):
                print(f"File '{local_file_path}' does not exist")
                return False

            file_name = os.path.basename(local_file_path)
            storage_key = f"{storage_location}/{file_name}"
            self.s3_client.upload_file(local_file_path, bucket_name, storage_key)
            print(f"File '{local_file_path}' uploaded to '{bucket_name}/{storage_key}'")
            return True
        except Exception as e:
            print_exception(e)
            return False

    async def upload_file_as_stream(self, storage_location: str, stream: BinaryIO, file_name: str):
        try:
            storage_key = f"{storage_location}/{file_name}"
            assert hasattr(stream, 'read') and hasattr(stream, 'seek'), "Stream must be a file-like object with read and seek methods"
            stream.seek(0)
            self.s3_client.upload_fileobj(stream, bucket_name, storage_key)
            print(f"File uploaded successfully to {bucket_name}/{file_name}")
            return True
        except Exception as e:
            print(f"Error in uploading file: {e}")
            return False

    async def upload_file_as_object(self, storage_location: str, content, file_name: str):
        try:
            storage_key = f"{storage_location}/{file_name}"
            self.s3_client.put_object(Body=content, Bucket=bucket_name, Key=storage_key)
            print(f"File uploaded to {bucket_name}/{file_name}")
            return True
        except Exception as e:
            print_exception(e)
            return False

    async def download_file_locally(self, storage_key: str, local_file_path: str):
        try:
            # Make sure the file path directory exists
            os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
            self.s3_client.download_file(bucket_name, storage_key, local_file_path)
            print(f"File downloaded from {bucket_name}/{storage_key} to {local_file_path}")
            return True
        except Exception as e:
            print_exception(e)
            return False

    async def download_file_as_stream(self, storage_key: str):
        try:
            response = self.s3_client.get_object(Bucket=bucket_name, Key=storage_key)
            stream = response['Body'] # This is a StreamingBody object

            # Or altenative implementation

            # if 'Body' not in response or response['Body'] is None:
            #     raise ValueError("Failed to retrieve file body from S3")
            # async def stream_file() -> AsyncIterable[bytes]:
            #     while True:
            #         chunk = response['Body'].read(1024)  # Read in chunks of 1024 bytes
            #         if not chunk:
            #             break
            #         yield chunk
            # stream = stream_file()

            print(f"File {storage_key} downloaded from {bucket_name} as stream")
            return stream
        except Exception as e:
            print_exception(e)
            return None

    async def download_file_as_object(self, storage_key: str) -> io.BytesIO:
        try:
            buffer = io.BytesIO()
            self.s3_client.download_fileobj(Bucket=bucket_name, Key=storage_key, Fileobj=buffer)
            buffer.seek(0)
            print(f"File {storage_key} downloaded from {bucket_name} as object")
            return buffer
        except Exception as e:
            print_exception(e)
            return None

###############################################################################
