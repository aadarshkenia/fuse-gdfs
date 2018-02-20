import ntpath
import os
import logging
import ConfigParser
from driveClient import FuseDriveClient

#TODO: Configure logger - This has been duplicated, refactor this.
formatter = logging.Formatter("%(asctime)s %(threadName)s %(levelname)s %(message)s")
logging.basicConfig(filename='fuse.log', level=logging.DEBUG, format='%(asctime)s %(threadName)s %(levelname)s %(message)s')

class FileUtils:
    def __init__(self, mountPoint):
        self.mount_point = mountPoint
        self.myAppConfig = self.load_configuration('../config/driveapi/app.properties')
        self.drive_client = FuseDriveClient(mountPoint=mountPoint)
        self.mountPointFolderIdOnDrive = self.get_mount_path_folder_id_on_drive()

    def get_file_name(self, filePath):
        return ntpath.basename(filePath)

    #IF a file path is something like x/y/file1.pdf, returns the folderId on Google Drive for the folder 'y'
    def get_folder_id_of_parent(self, filepath):
        root = '/'
        parent, child = ntpath.split(filepath)
        if(parent == root): #we are at the root level
            #Get folder id of root elem in mount point.
            #a. Get folder id of mount point on Google drive.
            return '1kT7GDQlHgIHonY1EitlNt39VbV4a3zaI' # Temporarily hardcoded. Change this to either return from config or load up during initialization.
        else:
            folder_id_of_parent = self.get_folder_id_of_parent(parent)
            children = self.drive_client.list_folder_items(folder_id=folder_id_of_parent)
            return self.get_folder_id_of_matching_child(children, child)

    def get_folder_id_of_matching_child(self, children, child):
        logging.info('Looking up child: %s in the list:', child, children)
        for childElem in children:
            if (childElem['name'] == child):
                logging.info('Child folder id=%s', childElem['id'])
                return childElem['id']
        raise RuntimeError('Cannot find child element with name:{} in the list of children: {}'.format(child, children))

    # Initialize the mount path folder ID on drive, if it already exists. If the folder path does not exists then create one.
    def get_mount_path_folder_id_on_drive(self):
        mountPath = self.myAppConfig['drive_mount_point_folder_path']
        logging.info('Mount path : %s', mountPath)
        paths = os.path.normpath(mountPath).strip(os.sep).split(os.sep)
        mountPointFolderId = self.create_folder_path_if_does_not_exist(paths)
        logging.info('Mount Path Folder Id initialized to: %s', mountPointFolderId)
        
    #Given a folder hierarchy, creates this hierarchy on drive if all the paths do not exist. If they exist, returns the folderId of last one (deepest child)
    def create_folder_path_if_does_not_exist(self, paths=[]):
        parentFolderId = 'root'
        for path in paths:
            items = self.drive_client.list_folder_items(parentFolderId) # TODO: This can be optimized if any of the parent folders did not exist.
            found = False
            times = 0
            for item in items:
                if(item['name'] == path):
                    parentFolderId = item['id']
                    found = True
                    times += 1
            if times > 1:
                raise RuntimeError("Found more than one folder with name: %s in path collection: %s.", path, items)
            if not found:
                parentFolderId = self.drive_client.create_folder(path, parentFolderId)
        return parentFolderId        
        
    #TODO: Refactor this to move it to a different module since its being repeated across driveClient and here.
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
    fileUtils = FileUtils('../mnt')
    parentId = fileUtils.get_folder_id_of_parent('/abc/abc-1')
    print ("Parent id of /abc: " + parentId)