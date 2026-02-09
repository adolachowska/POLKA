import os
from azure.storage.blob import BlobServiceClient
import uuid
from dotenv import load_dotenv

load_dotenv()

CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME = "raw-csv-uploads"

if not CONNECTION_STRING:
    raise ValueError("Brakuje AZURE_STORAGE_CONNECTION_STRING w pliku .env!")

# Inicjalizacja klienta (raz, globalnie)
blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)

def upload_file_to_blob(file_content: bytes, filename: str) -> str:
    unique_filename = f"{uuid.uuid4()}_{filename}"
    blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=unique_filename)
    blob_client.upload_blob(file_content, overwrite=True)
    return blob_client.url