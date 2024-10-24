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