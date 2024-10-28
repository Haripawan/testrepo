def upload_file(bucket_name, object_key, file_path):
    try:
        s3_client.upload_file(file_path, bucket_name, object_key)
        print(f"File '{file_path}' uploaded to '{bucket_name}/{object_key}'")
    except Exception as e:
        print(f"An error occurred while uploading the file: {e}")

def download_file(bucket_name, object_key, download_path):
    try:
        s3_client.download_file(bucket_name, object_key, download_path)
        print(f"File '{object_key}' downloaded from '{bucket_name}' to '{download_path}'")
    except Exception as e:
        print(f"An error occurred while downloading the file: {e}")

def list_files(bucket_name, folder_prefix):
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_prefix)
        if 'Contents' in response:
            files = [item['Key'] for item in response['Contents']]
            print("Files found:")
            for file in files:
                print(file)
            return files
        else:
            print("No files found in the specified folder.")
            return []
    except Exception as e:
        print(f"An error occurred while listing files: {e}")
        return []

def move_file(bucket_name, source_key, destination_key):
    try:
        # Copy the file to the new location
        s3_client.copy_object(
            Bucket=bucket_name,
            CopySource={'Bucket': bucket_name, 'Key': source_key},
            Key=destination_key
        )
        # Delete the original file
        s3_client.delete_object(Bucket=bucket_name, Key=source_key)
        print(f"File moved from '{source_key}' to '{destination_key}' in bucket '{bucket_name}'")
    except Exception as e:
        print(f"An error occurred while moving the file: {e}")

def copy_file(bucket_name, source_key, destination_key):
    try:
        s3_client.copy_object(
            Bucket=bucket_name,
            CopySource={'Bucket': bucket_name, 'Key': source_key},
            Key=destination_key
        )
        print(f"File copied from '{source_key}' to '{destination_key}' in bucket '{bucket_name}'")
    except Exception as e:
        print(f"An error occurred while copying the file: {e}")


bucket_name = "your-bucket-name"

# Upload a file
upload_file(bucket_name, "my-folder/file.txt", "/local/path/to/file.txt")

# Download a file
download_file(bucket_name, "my-folder/file.txt", "/local/path/to/downloaded_file.txt")

# List files in a folder
list_files(bucket_name, "my-folder/")

# Move a file
move_file(bucket_name, "my-folder/file.txt", "my-folder/new-folder/file_moved.txt")

# Copy a file
copy_file(bucket_name, "my-folder/file.txt", "my-folder/backup/file_copied.txt")

# Delete a file
delete_file(bucket_name, "my-folder/file.txt")

