from __future__ import print_function

import os.path

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from dotenv import load_dotenv

load_dotenv()

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive']

# The ID of a sample document.
DOCUMENT_ID = '195j9eDD3ccgjQRttHhJPymLJUCOUjs-jmwTrekvdjFE'


class GoogleDoc:

    def __init__(self, creds):
        """Shows basic usage of the Docs API.
        Prints the title of a sample document.
        """
        self.creds = creds
        try:
            self.service = build('docs', 'v1', credentials=self.creds)
            # Test doc service
            _test_doc = self.service.documents().get(documentId=DOCUMENT_ID).execute()
            print("Successfully retrieved 'creds' from env vars.")
        except RefreshError as e:
            try:
                self.creds = get_new_creds()
                print("Got creds from 'get_new_creds'")
                self.service = build('docs', 'v1', credentials=self.creds)
            except HttpError as err:
                print(err)

    @staticmethod
    def construct_content(text: str, img_file_id: str):
        text = text.split('\n')
        payload = []
        idx = 1
        for i, section in enumerate(text):
            if i == 0:
                new_section = section
                d = \
                    {
                        'insertText': {
                            'location': {
                                'index': idx
                            },
                            'text': new_section
                        }
                    }
            else:
                new_section = f'\n{section} '
                d = \
                    {
                        'insertText': {
                            'endOfSegmentLocation': {},
                            'text': new_section
                        }
                    }

            payload.append(d)

        if img_file_id:
            img_d = {
                'insertInlineImage': {
                    'endOfSegmentLocation': {},
                    'uri': img_file_id,
                    # f'https://drive.google.com/uc?export=view&id={img_file_id}',
                    'objectSize': {
                        'height': {
                            'magnitude': 300,
                            'unit': 'PT'
                        },
                        'width': {
                            'magnitude': 300,
                            'unit': 'PT'
                        }
                    }
                }
            }
            payload.append(img_d)
        return payload

    def create_doc(self, title: str, text: str, img_file_id: str) -> str:
        """Create full Google Doc."""
        folder_id = '162FkqqZbNCSDPxYfRmNjFeG1fcb2Nx_-'

        # Create new doc
        doc = self.service.documents().create(body={'title': title}).execute()
        doc_id = doc.get('documentId')

        # Upload image to GDrive
        # if img_file_name:
        #     img_file_id = move_image_to_folder(img_file_name=img_file_name, folder_id=folder_id)
        # else:
        #     img_file_id = ''

        # Add content to doc
        requests = self.construct_content(text, img_file_id)
        _ = self.service.documents().batchUpdate(documentId=doc_id,
                                                 body={'requests': requests}).execute()

        drive_service = _initialize_drive_service(self.creds)
        _parent_id = move_file_to_folder(service=drive_service,
                                         file_id=doc_id,
                                         folder_id=folder_id)

        # Make doc public
        doc_url = f'https://docs.google.com/document/d/{doc_id}'
        return doc_url, img_file_id


user_permission = {
    'type': 'anyone',
    'role': 'writer',
}


def get_creds():
    token = os.getenv('GOOGLE_TOKEN')
    refresh_token = os.getenv('REFRESH_TOKEN')
    id_token = os.getenv('ID_TOKEN')
    token_uri = os.getenv('TOKEN_URI')
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    creds = Credentials(token=token,
                        refresh_token=refresh_token,
                        id_token=id_token,
                        token_uri=token_uri,
                        client_id=client_id,
                        client_secret=client_secret,
                        scopes=SCOPES
                        )
    return creds


def get_new_creds():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    # creds = Credentials(_token)
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds


def _initialize_drive_service(creds):
    try:
        service = build('drive', 'v3', credentials=creds)
        # Test service
        results = service.files().list(
            pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])
    except RefreshError as e:
        try:
            creds = get_new_creds()
            service = build('drive', 'v3', credentials=creds)
        except HttpError as err:
            print(err)
    return service


def move_image_to_folder(service, img_file_name, folder_id):
    """Move image between Google Drive folders."""
    # Upload image file
    try:
        #
        file_metadata = {
            'name': img_file_name,
            'parent': folder_id
        }
        media = MediaFileUpload(img_file_name,
                                mimetype='image/png')
        # pylint: disable=maybe-no-member
        img_file = service.files().create(body=file_metadata, media_body=media,
                                          fields='id, parents').execute()
        img_file_id = img_file.get("id")
        _ = service.permissions().create(fileId=img_file_id, body=user_permission, fields='id').execute()
        print(F'File ID: {img_file.get("id")}')

    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None

    return img_file.get('id')


def move_file_to_folder(service, file_id, folder_id):
    """Move specified file to the specified folder.
    Args:
        file_id: Id of the file to move.
        folder_id: Id of the folder
    Print: An object containing the new parent folder and other meta data
    Returns : Parent Ids for the file

    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
    :param service:
    """

    try:
        # Edit permission
        try:
            permission = service.permissions().create(fileId=file_id, body=user_permission, fields='id').execute()
        except HttpError as error:
            print(F'An error occurred: {error}')
            file = None

        # pylint: disable=maybe-no-member
        # Retrieve the existing parents to remove
        file = service.files().get(fileId=file_id, fields='parents').execute()
        previous_parents = ",".join(file.get('parents'))
        # Move the file to the new folder
        file = service.files().update(fileId=file_id, addParents=folder_id,
                                      removeParents=previous_parents,
                                      fields='id, parents').execute()

        return file.get('parents')

    except HttpError as error:
        print(F'An error occurred: {error}')
        return None


def delete_gdrive_img_file(service, file_id):
    """Delete image from Google Drive."""
    file = service.files().delete(fileId=file_id).execute()
    return file


if __name__ == '__main__':
    gdoc = GoogleDoc()
    title = 'A test doc title'
    text = "My project, SmarTy, is an attempt to make life easier for knowledge workers in the modern attention economy. \nIt's a task planner that evaluates the importance and urgency of tasks, prioritizes them, and batches them together to reduce context switching fatigue. SmarTy works by providing example pairs of tasks and classes to the Cohere Classify API, which uses transfer learning to cluster new tasks into one of four categories: do it now, delegate, discard, or designate.\nThe output pairs are then fed into the Cohere Embed API to calculate string embeddings, which are bundled into similar batches using k-means.\nSmarTy provides value by allowing users to focus their energy on impactful goals, reduce contact switching fatigue, create opportunities for teamwork, and identify and eliminate unnecessary busy work."
    gdoc.create_doc(title, text)
