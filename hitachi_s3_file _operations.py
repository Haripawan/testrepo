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


def print_metadata(bucket_name, folder_prefix=None):
    try:
        # List all objects in the specified folder (or bucket root if folder_prefix is None)
        list_response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_prefix)

        if 'Contents' in list_response:
            for item in list_response['Contents']:
                object_key = item['Key']
                # Retrieve metadata for each object
                metadata_response = s3_client.head_object(Bucket=bucket_name, Key=object_key)

                print(f"Metadata for '{object_key}':")
                print(f"  Size: {metadata_response['ContentLength']} bytes")
                print(f"  Last Modified: {metadata_response['LastModified']}")
                print(f"  Content Type: {metadata_response['ContentType']}")

                # Print custom metadata, if any
                custom_metadata = metadata_response.get('Metadata', {})
                if custom_metadata:
                    print("  Custom Metadata:")
                    for key, value in custom_metadata.items():
                        print(f"    {key}: {value}")
                else:
                    print("  Custom Metadata: None")
                
                print("\n")
        else:
            print("No files or folders found in the specified location.")
            
    except Exception as e:
        print(f"An error occurred while fetching metadata: {e}")

# Example usage
bucket_name = "your-bucket-name"
folder_prefix = "my-folder/sub-folder/"  # Optional: specify folder path; use None for bucket root

# Call the function to print metadata for all files and folders
print_metadata(bucket_name, folder_prefix)


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


import boto3
from botocore.client import Config
import yaml

# Function to load YAML config
def load_yaml_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

# Load connection parameters from the connection_config.yaml file
connection_config = load_yaml_config('connection_config.yaml')

# Initialize the S3 client using connection details from the config file
s3_client = boto3.client(
    's3',
    endpoint_url=connection_config['connection']['endpoint_url'],
    aws_access_key_id=connection_config['connection']['aws_access_key_id'],
    aws_secret_access_key=connection_config['connection']['aws_secret_access_key'],
    config=Config(signature_version='s3v4'),
    verify=connection_config['connection']['verify_ssl']
)

def upload_file_with_metadata(bucket_name, object_key, file_path, custom_metadata=None):
    try:
        # Prepare the upload parameters
        upload_params = {
            'Bucket': bucket_name,
            'Key': object_key,
            'Filename': file_path,
        }

        # Include custom metadata if provided
        if custom_metadata:
            upload_params['Metadata'] = custom_metadata

        # Upload the file with or without metadata
        s3_client.upload_file(**upload_params)
        
        print(f"File '{file_path}' uploaded to '{bucket_name}/{object_key}' with metadata: {custom_metadata or 'None'}")
        
    except Exception as e:
        print(f"An error occurred while uploading the file: {e}")

# Example usage
bucket_name = "your-bucket-name"
object_key = "my-folder/sub-folder/file.txt"
file_path = "/local/path/to/file.txt"

# Optional custom metadata
custom_metadata = {
    "author": "user1",
    "project": "project-name"
}

# Call the function to upload the file with optional custom metadata
upload_file_with_metadata(bucket_name, object_key, file_path, custom_metadata)


