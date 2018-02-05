import logging
import httplib2

from googleapiclient.discovery import build,HttpRequest
from googleapiclient.http import build_http
from oauth2client.service_account import ServiceAccountCredentials

SERVICE_ACCOUNT_FILE = '../config/driveapi/service-account-key.json'
SCOPES = ['https://www.googleapis.com/auth/drive']
DISCOVERY_URI = ('https://www.googleapis.com/discovery/v1/apis/drive/v3/rest')

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

credentials = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, SCOPES)
drive_service = build('drive', 'v3', http=None, discoveryServiceUrl=DISCOVERY_URI, developerKey=None, model=None,
                          requestBuilder=HttpRequest, credentials=credentials, cache_discovery=True, cache=None)

def main():
    param = {}
    list_folder_items(drive_service, '0', param)

def create_folder(service, foldername):
    metadata = {
        'name': foldername,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    file = service.files().create(body=metadata, fields='id').execute()
    print 'Folder id: %s' % file.get('id')

def list_folder_items(service, folderId, param):
    files = service.files().list(**param).execute()
    print files
    for item in files['files']:
       print item['name'] + " " + item['id']

if __name__ == '__main__':
    main()