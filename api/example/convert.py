import os
import time
import json
import subprocess

METADATA_FILE = 'file_metadata.json'

def load_metadata():
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_metadata(metadata):
    with open(METADATA_FILE, 'w') as f:
        json.dump(metadata, f)

def convert_dos_to_unix(file_path):
    try:
        result = subprocess.run(['dos2unix', file_path], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout = result.stdout.decode('utf-8')
        stderr = result.stderr.decode('utf-8')
        print(f"Converted {file_path} to UNIX format.\nOutput: {stdout}\nError: {stderr}")
    except subprocess.CalledProcessError as e:
        stdout = e.stdout.decode('utf-8')
        stderr = e.stderr.decode('utf-8')
        print(f"Error converting {file_path}:\nOutput: {stdout}\nError: {stderr}")

def scan_and_convert(directory, metadata):
    current_files = {os.path.join(root, file): os.path.getmtime(os.path.join(root, file))
                     for root, dirs, files in os.walk(directory) for file in files}
    
    # Check for new or modified files
    for file_path, mtime in current_files.items():
        if file_path not in metadata or metadata[file_path] != mtime:
            convert_dos_to_unix(file_path)
            metadata[file_path] = mtime

    # Remove entries for files that no longer exist
    for file_path in list(metadata.keys()):
        if file_path not in current_files:
            del metadata[file_path]

if __name__ == "__main__":
    directory_to_watch = "/home/pbr/database/"
    metadata = load_metadata()

    try:
        while True:
            scan_and_convert(directory_to_watch, metadata)
            save_metadata(metadata)
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping the monitoring script.")
        save_metadata(metadata)
