import boto3
from botocore.client import Config

# Initialize the session
session = boto3.session.Session()

# S3 client for Hitachi Vantara's S3-compatible service
s3_client = session.client(
    's3',
    endpoint_url='https://your-hitachi-vantara-s3-endpoint.com',  # Replace with your endpoint
    aws_access_key_id='your-access-key',                          # Replace with your access key
    aws_secret_access_key='your-secret-key',                      # Replace with your secret key
    config=Config(signature_version='s3v4')  # Ensure S3v4 signature is used
)

# Function to create a folder in S3
def create_folder(bucket_name, folder_name):
    # Folders are represented as objects with '/' at the end of the key
    folder_key = folder_name if folder_name.endswith('/') else folder_name + '/'
    
    # Create the folder by uploading a zero-byte object with the folder name
    s3_client.put_object(Bucket=bucket_name, Key=folder_key)
    print(f"Folder '{folder_name}' created in bucket '{bucket_name}'")

# Example usage
bucket_name = 'your-bucket-name'  # Replace with your S3 bucket name
folder_name = 'my-folder/sub-folder'  # Replace with the folder path you want to create

# Create the folder
create_folder(bucket_name, folder_name)


##################

import boto3
from botocore.client import Config

# Initialize the S3 client for Hitachi Vantara's S3-compatible service
s3_client = boto3.client(
    's3',
    endpoint_url='https://your-hitachi-vantara-s3-endpoint.com',  # Replace with your endpoint
    aws_access_key_id='your-access-key',                          # Replace with your access key
    aws_secret_access_key='your-secret-key',                      # Replace with your secret key
    config=Config(signature_version='s3v4'),
    verify=False  # Disable SSL verification if needed
)

# Function to upload a file to a specific folder
def upload_file_to_folder(bucket_name, folder_name, file_path, object_name=None):
    # Ensure the folder name ends with a slash ('/') to specify a folder path
    folder_key = folder_name if folder_name.endswith('/') else folder_name + '/'
    
    # Object name is the file name if not provided
    if object_name is None:
        object_name = file_path.split('/')[-1]  # Extract the file name from the file path
    
    # Full key will include the folder path and the object (file) name
    key = folder_key + object_name
    
    # Upload the file
    s3_client.upload_file(file_path, bucket_name, key)
    print(f"File '{file_path}' uploaded to folder '{folder_name}' in bucket '{bucket_name}' as '{key}'")

# Example usage
bucket_name = 'your-bucket-name'  # Replace with your S3 bucket name
folder_name = 'my-folder/sub-folder'  # Replace with the folder path you want to upload to
file_path = '/path/to/your/local/file.txt'  # Replace with the path to your local file
object_name = 'custom_file_name.txt'  # Optional: Replace with a custom name for the uploaded object

# Upload the file to the specific folder
upload_file_to_folder(bucket_name, folder_name, file_path, object_name)

