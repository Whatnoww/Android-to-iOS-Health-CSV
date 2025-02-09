#!/usr/bin/env python3
from __future__ import print_function
import os
import io
import pickle
import subprocess
import re

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']

def get_drive_service():
    """
    Authenticate and create the Google Drive API service.
    It uses a local webserver for authentication and stores the token in token.pickle.
    """
    creds = None
    # Check if token already exists
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If no (valid) credentials, go through the OAuth flow.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Ensure you have your credentials.json file downloaded from Google Cloud Console.
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for next time.
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('drive', 'v3', credentials=creds)
    return service

def list_files(service, folder_id=None):
    """
    List files from Google Drive.
    If folder_id is provided, only files in that folder are returned.
    By default, all non-folder files in your drive are returned.
    """
    # Query for non-folder files.
    query = "mimeType != 'application/vnd.google-apps.folder'"
    if folder_id:
        query = f"'{folder_id}' in parents and {query}"
    results = service.files().list(q=query, fields="nextPageToken, files(id, name)").execute()
    return results.get('files', [])

def load_downloaded_ids(filename='downloaded.txt'):
    """
    Load the set of file IDs that have been previously downloaded.
    """
    if not os.path.exists(filename):
        return set()
    with open(filename, 'r') as f:
        return set(line.strip() for line in f if line.strip())

def add_downloaded_id(file_id, filename='downloaded.txt'):
    """
    Append a new file ID to the downloaded.txt file.
    """
    with open(filename, 'a') as f:
        f.write(file_id + "\n")

def sanitize_filename(filename):
    # Replace any character that is not allowed with an underscore.
    # The regex pattern below matches any of the characters: \ / : * ? " < > |
    return re.sub(r'[\\/*?:"<>|]', "_", filename)

def download_file(service, file_id, file_name, download_folder='input_csvs'):
    # Ensure the download folder exists
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    # Sanitize the filename to remove any invalid characters
    safe_file_name = sanitize_filename(file_name)
    file_path = os.path.join(download_folder, safe_file_name)

    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(file_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    print(f"Downloading {file_name} as {safe_file_name}...")
    while not done:
        status, done = downloader.next_chunk()
        if status:
            print(f"Download {int(status.progress() * 100)}% complete.")
    print("Download complete.")
    return file_path

def delete_file(service, file_id):
    """
    Delete a file from Google Drive.
    """
    service.files().delete(fileId=file_id).execute()
    print(f"Deleted file (ID: {file_id}) from Drive.")

def execute_script(script_path, args):
    """
    Execute another Python script with the given list of arguments.
    """
    command = ['python', script_path] + args
    print(f"Executing script: {' '.join(command)}")
    subprocess.run(command)

def main():
    # Create the Google Drive API service.
    service = get_drive_service()

    # Load previously downloaded file IDs.
    downloaded_ids = load_downloaded_ids()

    # Optionally, if you want to restrict to a particular folder, set folder_id to that folder's ID.
    folder_id = "1vHvNjrYhKsheThTcL_Kz476v77V76Nq4"  # Replace with your actual folder ID
    files = list_files(service, folder_id)

    if not files:
        print("No files found in Google Drive.")

    # Specify the Python script you wish to execute and any base arguments.
    script_to_execute = "convert_sleep_csvs.py"  # Replace with your target script
    base_script_args = ["./input_csvs", "./converted_csvs"]  # Replace with your desired arguments

    # List to hold the paths of newly downloaded files
    downloaded_files = []

    for file in files:
        file_id = file['id']
        file_name = file['name']
        print(f"Found file: {file_name} (ID: {file_id})")

        if file_id in downloaded_ids:
            # Already processed file: simply delete it from Drive.
            print("File was already downloaded previously; deleting from Drive.")
            try:
                delete_file(service, file_id)
            except Exception as e:
                print(f"Error deleting file {file_name}: {e}")
            continue

        # Download the file since it has not been processed before.
        try:
            local_file_path = download_file(service, file_id, file_name)
        except Exception as e:
            print(f"Error downloading file {file_name}: {e}")
            continue

        # Record that we’ve processed this file.
        add_downloaded_id(file_id)

        # Delete the file from Drive.
        try:
            delete_file(service, file_id)
        except Exception as e:
            print(f"Error deleting file {file_name} from Drive: {e}")

        # Collect the local file path for later processing.
        downloaded_files.append(local_file_path)

    # Execute the external script only once after processing all files.
    if downloaded_files:
        # You can pass all downloaded file paths as arguments along with base arguments.
        # Adjust this if your called script expects a different format.
        script_args = base_script_args
        execute_script(script_to_execute, script_args)
    else:
        print("No new files downloaded. Skipping execution of the external script.")
        script_args = base_script_args
        execute_script(script_to_execute, script_args)

if __name__ == '__main__':
    main()
