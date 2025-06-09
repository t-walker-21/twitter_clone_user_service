from minio import Minio
import os

class MinioClient:
    def __init__(self):
        self.client = Minio(
            os.environ.get("MINIO_ENDPOINT", "localhost:9000"),
            access_key=os.environ.get("MINIO_ACCESS_KEY", "kxti25Wx321AGVuq8jpN"),
            secret_key=os.environ.get("MINIO_SECRET_KEY", "ktMHR4qSYuH2KvtqbaWL857CVkDPTfCxmrEOYcbc"),
            secure=False  # Set to True if using HTTPS
        )

    def get_client(self):
        return self.client