from azure.storage.blob import BlobServiceClient
import pyodbc

# 1. Kontener
try:
    svc = BlobServiceClient.from_connection_string("UseDevelopmentStorage=true")
    svc.create_container("raw-csv-uploads")
    print("✅ Kontener utworzony.")
except Exception:
    print("✅ Kontener już istnieje.")

# 2. Baza
try:
    conn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost\\SQLEXPRESS;DATABASE=master;Trusted_Connection=yes;TrustServerCertificate=yes', autocommit=True)
    conn.cursor().execute("IF NOT EXISTS(SELECT * FROM sys.databases WHERE name='polka_db') CREATE DATABASE polka_db")
    print("✅ Baza SQL utworzona.")
except Exception as e:
    print(f"⚠️ Info o bazie: {e}")

    #http://127.0.0.1:8000/docs
    #python -m uvicorn main:app --reload
