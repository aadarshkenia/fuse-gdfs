import ConfigParser
import logging

from googleapiclient.discovery import build,HttpRequest
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.http import MediaFileUpload
from oauth2client.service_account import ServiceAccountCredentials

# Configure logger.
formatter = logging.Formatter("%(asctime)s %(threadName)s %(levelname)s %(message)s")
logging.basicConfig(filename='fuse.log', level=logging.DEBUG, format='%(asctime)s %(threadName)s %(levelname)s %(message)s')
rootFolderId = 'root'

class FuseDriveClient:

    def __init__(self, mountPoint):
        try:
            self.mountPoint = mountPoint
            self.myAppConfig = self.load_configuration('../config/driveapi/app.properties')

            self.drive_client_service = self.build_drive_client_service()
        except Exception as e:
            logging.error("Error initializing the app. %s %s", e.message, e.__doc__)




    def build_drive_client_service(self):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(self.myAppConfig['service_account_file'], self.myAppConfig['scopes'])
        drive_service = build('drive', 'v3', http=None, discoveryServiceUrl=self.myAppConfig['discovery_uri'], developerKey=None, model=None,
                              requestBuilder=HttpRequest, credentials=credentials, cache_discovery=True, cache=None)
        return drive_service

    # Creates a new folder and returns its id.
    def create_folder(self, foldername, parentFolderId):
        logging.info('Received create_folder request with folderName:{} parent:{}'.format(foldername, parentFolderId))
        metadata = {
            'name': foldername,
            'mimeType': 'application/vnd.google-apps.folder', #TODO: Default mime type for folders, maybe move to an enum ?
            'parents' : [parentFolderId]
        }
        file = self.drive_client_service.files().create(body=metadata, fields='id').execute()
        fileId =  file.get('id')
        logging.info('Successfully created folder:%s , fileId: %s', foldername, fileId)
        return fileId


    # Lists all items inside the folder with id=folderId, returns a list of 'files' resource.
    def list_folder_items(self, folder_id, param={}):
        query = '\'' + folder_id +'\'' + ' in parents'
        files = self.drive_client_service.files().list(q=query, **param).execute()

        return files['files']

    # Creates a  new file and returns its ID.
    def upload_file(self, file, fileName, title, parentId, mimeType):
        """
        :param file: file object for the file to be uploaded
        :param fileName:
        :param parentId: parent folder Id on Drive
        :param mimeType:
        :return: returns the ID of the uploaded file.
        """
        metadata = {
            'name' : fileName,
            'mimeType' : mimeType,
            'parents' : [parentId],
            'title': title
        }
        media = MediaIoBaseUpload(file, mimeType)
        file = self.drive_client_service.files().create(media_body=media, body=metadata).execute()
        fileId = file.get('id')
        logging.info('Successfully uploaded file :%s , fileId: %s', fileName, fileId)
        return fileId

    def get_file_metadata(self, fileId):
        logging.info('Received GET metadata request for fileId: %s', fileId)
        metadata = self.drive_client_service.files().get(fileId=fileId).execute()
        logging.info('Metadata: %s', metadata)
        return metadata

    # Updates basic metadata for a file like new name(title), description, etc as provided in metadata map.
    def update_file_metadata(self, fileId, metadata):
        logging.info('Received update metadata request for fileId: {} map: {}'.format(fileId, metadata))
        originalMetadata = self.get_file_metadata(fileId)
        possibleUpdateKeys = ['title', 'description', 'parents']
        for key in possibleUpdateKeys:
            if key in metadata:
                originalMetadata[key] = metadata[key]

        updatedMetadata = self.drive_client_service.files().update(
            fileId=fileId,
            body=originalMetadata).execute()
        logging.info('Updated file metadata: %s', updatedMetadata)
        return updatedMetadata

    # Deletes a file or folder
    def delete_file(self, fileId):
        file = self.drive_client_service.files().delete(fileId=fileId).execute()

    # Utility function to delete all files in root folder
    def delete_everything(self):
        allItems = self.list_folder_items(rootFolderId)
        for item in allItems:
            itemId = item['id']
            self.delete_file(itemId)

    # Utility function to print the folder tree starting from root and onwards to console.
    def print_folder_tree(self, parentFolderId):
        self.print_folder_tree_util(parentFolderId, 0)

    def print_folder_tree_util(self, parentFolderId, indent):
        allItems = self.list_folder_items(parentFolderId)
        for item in allItems:
            print ('{}{}'.format(' ' * indent, item['name']))
            if(item['mimeType'] == 'application/vnd.google-apps.folder'): #TODO: move to enum
                self.print_folder_tree_util(item['id'], indent + 2)

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
    fuseDriveClient = FuseDriveClient('tmpdir')
    # file = open("../fuse_action_items.txt")
    # fileId = fuseDriveClient.upload_file(file, 'f1.txt', 'f1.txt', ['root'], 'application/vnd.google-apps.file')
    fileId = '1RRqW2sbBuagkuGp3nu_bKV7zohnv4F8XPQJ-2aRPcss'
    newmetadata = {}
    newmetadata['title'] = 'f1-renamed.txt'
    updatedMetadata = fuseDriveClient.update_file_metadata(fileId, newmetadata)
    fuseDriveClient.get_file_metadata(fileId)
    params = {}
    # fuseDriveClient.delete_everything()
    # fuseDriveClient.create_folder('v1', '1kT7GDQlHgIHonY1EitlNt39VbV4a3zaI') # mnt = 1kT7GDQlHgIHonY1EitlNt39VbV4a3zaI
    # files = fuseDriveClient.list_folder_items(folder_id='1gyuC_KvJo5VbU-tDGzUyOfQbbD2TBKwE', param=params)
    # for file1 in files:
    #     print file1['id'] + ' : ' + file1['name']
    fuseDriveClient.print_folder_tree(rootFolderId)
    # fuseDriveClient.delete_file('1Z0ln9BT6tCgPl_7fWqyr30OLMI_Lbzty')
