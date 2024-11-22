from google.cloud import storage


def download_blob(bucket_name, source_blob_name, destination_file_name):

    storage_client = storage.Client.from_service_account_json('credentials.json')
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

    print(f"Le fichier {source_blob_name} a été téléchargé et sauvegardé en {destination_file_name}.")


if __name__ == '__main__':
    bucket_name = "bucket-ollama"
    source_blob_name = "file-ollama/exemple1.pdf"
    destination_file_name = "downloadData/exemple_local.pdf"
    download_blob(bucket_name, source_blob_name, destination_file_name)
