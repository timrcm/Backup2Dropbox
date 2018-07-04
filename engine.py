# DirBak
# Takes an environment path and backs it up to Dropbox
# 7/1/2018 TimRCM

import datetime
import os
from sys import argv

import dropbox as db

import config
import notifications

script, target, style, name, requested_path = argv
dbx = db.Dropbox(config.dbxAccount)

def timestamp():
    '''Generates the current timestamp based on system time'''
    return '{:%Y-%m-%d %H-%M-%S}'.format(datetime.datetime.now())

class dropbox(object):
    # Add functions for backup, sync, restore(?).. 
    # and add another class for S3 buckets as an alternative target?

    def __init__(self):
        self.target = target
        self.style = style
        self.name = name
        self.requested_path = requested_path

        self.timestamp = timestamp()

        if self.style == "backup":
            self.backup()
        elif self.style == "sync":
            self.sync()
        else:
            self.err = f"Unknown backup style for target {target}."
            notifications.smtp(self.name, self.requested_path, self.timestamp, self.err)

    def __call__(self):
        pass

    def backup(self):
        '''Initiates a backup of the given path to Dropbox'''

        for dirName, subdirList, fileList in os.walk(self.requested_path):
            for file in fileList:
                self.file_path = os.path.join(dirName, file)

                try:
                    # Cut out all preceding directories from the remote path
                    self.remote_path = dirName.replace(self.requested_path, '')
                    self.remote_path_correction = ''

                    # If the remote path is no longer empty (IE if we've entered a subdir)
                    # replace Windows' backslash nonsense with a forward slash, 
                    # remove any duplicate forward slashes, and add a trailing forward slash 
                    if self.remote_path != '':
                        self.remote_path_winfix = self.remote_path.replace('\\', '/') # stupid Windows...
                        self.remote_path_correction = self.remote_path_winfix.replace('//', '/')
                        self.remote_path_correction += '/'

                    with open(self.file_path, mode='rb') as f:
                        # Ugly spaghetti fix for pathing issues caused by the Windows fix
                        if self.remote_path_correction == '':
                            self.pathfixer = '/'
                        else:
                            self.pathfixer = ''
                        # Upload the given path to a remote Dropbox path 
                        dbx.files_upload(f.read(), path=f'/{self.name}/{self.timestamp}{self.pathfixer}{self.remote_path_correction}{file}')
                    
                    print(f"Uploaded '{self.name}': {self.file_path} at {self.timestamp}")

                # Send a notification if something failed 
                except Exception as err:
                    print(f'Failed to upload {file}, {err}')
                    notifications.smtp(self.name, self.file_path, self.timestamp, err)


    def sync(self):
        pass

    def cleanup(self):
        pass


class b2(object):

    def __init__(self):
        self.target = target
        self.style = style
        self.name = name
        self.requested_path = requested_path

        self.timestamp = timestamp()

    def __call__(self):
        pass

    def backup(self):
        pass

    def sync(self):
        pass

    def cleanup(self):
        pass
