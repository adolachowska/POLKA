import os
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError
import uuid
from dotenv import load_dotenv

load_dotenv()

CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME = "raw-csv-uploads"

if not CONNECTION_STRING:
    raise ValueError("Missing AZURE_STORAGE_CONNECTION_STRING in the .env file!")

blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)


def upload_file_to_blob(file_content: bytes, filename: str) -> str:
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)
    try:
        container_client.create_container()
        print(f"☁️ Created a new container in Azurite: {CONTAINER_NAME}")
    except ResourceExistsError:
        pass

    unique_filename = f"{uuid.uuid4()}_{filename}"

    blob_client = container_client.get_blob_client(blob=unique_filename)

    blob_client.upload_blob(file_content, overwrite=True)

    return blob_client.url