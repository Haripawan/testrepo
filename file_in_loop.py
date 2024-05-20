import os
import glob

# Define the directory path containing the files
directory_path = 'path/to/your/directory'

# Get a list of all files in the directory
file_list = glob.glob(os.path.join(directory_path, '*'))

# Loop through each file in the directory
for file_path in file_list:
    # Extract the file name from the file path
    file_name = os.path.basename(file_path)
    
    # Print the file name
    print(f'Processing file: {file_name}')
    
    # Open the file and read its content
    with open(file_path, 'r') as file:
        file_content = file.read()
        
        # Process the file content
        # (Replace this with your actual processing logic)
        print(f'File content:\n{file_content}\n')

# Example processing function
def process_file_content(content):
    # Add your processing logic here
    # For demonstration, just return the content length
    return len(content)

# Process each file
for file_path in file_list:
    with open(file_path, 'r') as file:
        file_content = file.read()
        result = process_file_content(file_content)
        print(f'Processed result for {os.path.basename(file_path)}: {result}')