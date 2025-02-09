import os
import pickle
import logging
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Setup logging to write to logs.txt
logging.basicConfig(
    filename='logs.txt',
    filemode='a',  # Append mode; use 'w' to overwrite each time
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# If modifying these SCOPES, delete the token.pickle file.
SCOPES = ['https://www.googleapis.com/auth/drive']

def main():
    try:
        # Authenticate and build the Drive API service.
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
    
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
    
        service = build('drive', 'v3', credentials=creds)
    
        # Define the target folder ID and file name.
        folder_id = "1UnayiVsRR8eAcfzTtEGBLchK-jgPnSPH"  # Replace with your target folder ID
        file_name = "combined.csv"
    
        # Query to find any existing file with the same name in the specified folder.
        query = f"name = '{file_name}' and '{folder_id}' in parents and trashed=false"
        results = service.files().list(q=query, fields="files(id, name)").execute()
        items = results.get('files', [])
    
        # Delete any found file(s).
        if items:
            for item in items:
                service.files().delete(fileId=item['id']).execute()
                logging.info(f"Deleted old file: {item['name']} (ID: {item['id']})")
        else:
            logging.info("No old file found to delete.")
    
        # Prepare metadata and media for the new file.
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }
        file_path = os.path.join("combined", file_name)
        media = MediaFileUpload(file_path, mimetype='text/csv')
    
        # Upload the new file.
        uploaded_file = service.files().create(
            body=file_metadata, 
            media_body=media, 
            fields='id'
        ).execute()
    
        logging.info(f'File uploaded successfully. File ID: {uploaded_file.get("id")}')
        logging.info("Script completed successfully.")
    except Exception as e:
        logging.error(f"Script encountered an error: {str(e)}")

if __name__ == '__main__':
    main()
