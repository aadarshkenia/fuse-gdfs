import ntpath
from driveClient import FuseDriveClient

class FileUtils:
    def __init__(self, mountPoint):
        self.mount_point = mountPoint
        self.drive_client = FuseDriveClient(mountPoint=mountPoint)

    def get_file_name(self, filePath):
        return ntpath.basename(filePath)

    #IF a file path is something like x/y/file1.pdf, returns the folderId on Google Drive for the folder 'y'
    def get_folder_id_of_parent(self, filepath):
        root = '/'
        filenames = []
        parent, child = ntpath.split(filepath)
        if(parent == root): #we are at the root level
            #Get folder id of root elem in mount point.
            #a. Get folder id of mount point on Google drive.
            return '1kT7GDQlHgIHonY1EitlNt39VbV4a3zaI' # Temporarily hardcoded. Change this to either return from config or load up during initialization.
        else:
            folder_id_of_parent = self.get_folder_id_of_parent(parent)
            children = self.drive_client.list_folder_items(folder_id=folder_id_of_parent)
            return self.get_folder_id_of_matching_child(child, children)

    def get_folder_id_of_matching_child(self, children, child):
        for childElem in children:
            if (childElem['name'] == child):
                return childElem['id']
        raise RuntimeError('Cannot find child element with name:{} in the list of children: {}', child, children)

if __name__ == '__main__':
    fileUtils = FileUtils('../mnt')
    parentId = fileUtils.get_folder_id_of_parent('/abc/abc-1')
    print ("Parent id of /abc: " + parentId)