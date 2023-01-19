from azure.storage.blob import generate_blob_sas, BlobSasPermissions
from azure.storage.filedatalake import (
    AccountSasPermissions,
    ContentSettings,
    DataLakeDirectoryClient,
    DataLakeFileClient,
    DataLakeServiceClient,
    EncryptionScopeOptions,
    FileSasPermissions,
    FileSystemClient,
    FileSystemSasPermissions,
    generate_account_sas,
    generate_file_sas,
    generate_file_system_sas,
    ResourceTypes
)
from datetime import datetime, timedelta


AZURE_ACC_NAME = "dlssdfsandbox"
AZURE_PRIMARY_KEY = "hnbCnarDj4A1lWDMWuZ4xcl94tXGQKWBTfDDG3A8NREAvJwMJBiu7i9nmxxCj4jp191pfK4xF3oRkh6uKFSz5Q=="
AZURE_CONTAINER = "dls"

token = generate_file_system_sas(
    AZURE_ACC_NAME,
    AZURE_CONTAINER,
    AZURE_PRIMARY_KEY,
    FileSystemSasPermissions(write=True, read=True, delete=True),
    datetime.utcnow() + timedelta(days=30),
)

file_client = DataLakeFileClient(
    account_url="{}://{}.dfs.core.windows.net".format(
        "https", AZURE_ACC_NAME),  # type: str
    file_system_name=AZURE_CONTAINER,  # type: str
    file_path="SpatialDB/processed/surface_coordinates/BG4FROST_GULLFAKS/images/5098.jpg",  # type: str
    credential=token)

print(file_client.url)


def generate_sas_token(file_name):
    sas = generate_blob_sas(account_name=AZURE_ACC_NAME,
                            account_key=AZURE_PRIMARY_KEY,
                            container_name=AZURE_CONTAINER,
                            blob_name=file_name,
                            permission=BlobSasPermissions(read=True),
                            expiry=datetime.utcnow() + timedelta(days=30))

    sas_url = 'https://'+AZURE_ACC_NAME+'.blob.core.windows.net/' + \
        AZURE_CONTAINER+'/SpatialDB/processed/surface_coordinates/BG4FROST_GULLFAKS/images/'+file_name+'?'+sas
    return sas_url


x = generate_sas_token('5098.png')
