from typing import AsyncIterable
import boto3
from botocore.exceptions import NoCredentialsError

class S3Storage:
    def __init__(self, 
                 aws_access_key_id, 
                 aws_secret_access_key,
                 region_name):
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )

    async def upload_file(self, file_name, bucket_name, s3_file_name=None):
        if s3_file_name is None:
            s3_file_name = file_name

        try:
            self.s3.upload_file(file_name, bucket_name, s3_file_name)
            print(f"File {file_name} uploaded to {bucket_name}/{s3_file_name}")
            return True
        except FileNotFoundError:
            print("The file was not found")
            return False
        except NoCredentialsError:
            print("Credentials not available")
            return False
        except Exception as e:
            print(f"Error in uploading reprt: {e}")
            return False

    async def upload_object(self, content, bucket_name, s3_file_name=None):
        try:
            self.s3.put_object(Body=content, Bucket=bucket_name, Key=s3_file_name)
            print(f"File {s3_file_name} uploaded to {bucket_name}/{s3_file_name}")
            return True
        except Exception as e:
            print(f"Error in uploading reprt: {e}")
        
    async def upload_excel_or_pdf(self, content, bucket_name, s3_file_name=None):
        try:
            self.s3.upload_fileobj(content, bucket_name, s3_file_name)
            print(f"File {s3_file_name} uploaded to {bucket_name}/{s3_file_name}")
            return True
        except Exception as e:
            print(f"Error in uploading reprt: {e}")

    async def download_file_as_stream(self, bucket_name, s3_file_name):
        try:
            response = self.s3.get_object(Bucket=bucket_name, Key=s3_file_name)
            if 'Body' not in response or response['Body'] is None:
                raise ValueError("Failed to retrieve file body from S3")
            async def stream_file() -> AsyncIterable[bytes]:
                while True:
                    chunk = response['Body'].read(1024)  # Read in chunks of 1024 bytes
                    if not chunk:
                        break
                    yield chunk
            file_content = stream_file()
            print(f"File {s3_file_name} downloaded from {bucket_name} as stream")
            return file_content
        except NoCredentialsError:
            print("Credentials not available")
            return None
        except Exception as e:
            print(f"Error in downloading file: {e}")
            return None

    