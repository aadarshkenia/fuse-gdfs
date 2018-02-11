import ConfigParser
import logging

from googleapiclient.discovery import build,HttpRequest
from oauth2client.service_account import ServiceAccountCredentials

#Configure logger.
formatter = logging.Formatter("%(asctime)s %(threadName)s %(levelname)s %(message)s")
logging.basicConfig(filename='fuse.log', level=logging.DEBUG, format='%(asctime)s %(threadName)s %(levelname)s %(message)s')

class  FuseGDFS:
    'A user space file system module that backs up to Google Drive.'

    def __init__(self, mountPoint):
        try:
            self.mountPoint = mountPoint;
            self.myAppConfig = self.load_configuration('../config/driveapi/app.properties')
            self.drive_client = self.build_drive_client_service()
        except Exception as e:
            logging.error("Error initializing the app. %s %s", e.message, e.__doc__)

    def build_drive_client_service(self):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(self.myAppConfig['service_account_file'], self.myAppConfig['scopes'])
        drive_service = build('drive', 'v3', http=None, discoveryServiceUrl=self.myAppConfig['discovery_uri'], developerKey=None, model=None,
                              requestBuilder=HttpRequest, credentials=credentials, cache_discovery=True, cache=None)
        return drive_service

    def create_folder(self, drive_client_service, foldername):
        metadata = {
            'name': foldername,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        file = drive_client_service.files().create(body=metadata, fields='id').execute()
        print 'Folder id: %s' % file.get('id')

    def list_folder_items(self, drive_client_service, folderId, param):
        files = drive_client_service.files().list(**param).execute()
        for item in files['files']:
           print item['name'] + " " + item['id']

    def load_configuration(self, filename):
        section = 'SectionOne'
        configDictionary = {}
        Config = ConfigParser.ConfigParser()
        Config.read('../config/driveapi/app.properties')
        options = Config.options(section)
        for option in options:
            configDictionary[option] = Config.get(section, option)
        logging.debug('GDrive configuration initialized to: %s', configDictionary)
        return configDictionary


if __name__ == '__main__':
    fuse = FuseGDFS('tmpdir')