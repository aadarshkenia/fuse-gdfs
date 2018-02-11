import logging
import httplib2
import ConfigParser
from googleapiclient.discovery import build,HttpRequest
from googleapiclient.http import build_http
from oauth2client.service_account import ServiceAccountCredentials

SERVICE_ACCOUNT_FILE = '../config/driveapi/service-account-key.json'
SCOPES = ['https://www.googleapis.com/auth/drive']
DISCOVERY_URI = ('https://www.googleapis.com/discovery/v1/apis/drive/v3/rest')

#Configure logger.
formatter = logging.Formatter("%(asctime)s %(threadName)s %(levelname)s %(message)s")
logging.basicConfig(filename='fuse.log', level=logging.DEBUG, format='%(asctime)s %(threadName)s %(levelname)s %(message)s')



credentials = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, SCOPES)
drive_service = build('drive', 'v3', http=None, discoveryServiceUrl=DISCOVERY_URI, developerKey=None, model=None,
                          requestBuilder=HttpRequest, credentials=credentials, cache_discovery=True, cache=None)

def main():
    param = {}
    # list_folder_items(drive_service, '0', param)
    load_configuration('../config/driveapi/app.properties')

def create_folder(service, foldername):
    metadata = {
        'name': foldername,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    file = service.files().create(body=metadata, fields='id').execute()
    print 'Folder id: %s' % file.get('id')

def list_folder_items(service, folderId, param):
    files = service.files().list(**param).execute()
    for item in files['files']:
       print item['name'] + " " + item['id']

def load_configuration(filename):
    section = 'SectionOne'
    configDictionary = {}
    Config = ConfigParser.ConfigParser()
    Config.read('../config/driveapi/app.properties')
    options = Config.options(section)
    for option in options:
        configDictionary[option] = Config.get(section, option)
    print configDictionary
    print configDictionary['service_account_file']
    logging.debug('GDrive configuration initialized to: %s', configDictionary)
    return configDictionary;

if __name__ == '__main__':
    main()