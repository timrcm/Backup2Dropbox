# DirBak
# Takes an environment path and backs it up to Dropbox
# 7/1/2018 TimRCM

import datetime
import os
from sys import argv

import dropbox as db

import config
import notifications

script, name, requested_path = argv
dbx = db.Dropbox(config.dbxAccount)

class dropbox(object):
    # Add functions for backup, sync, restore(?).. 
    # and add another class for S3 buckets as an alternative target?

    def __init__(self):
        self.name = name
        self.requested_path = requested_path

    def backup(self):
        pass

    def sync(self):
        pass


class b2(object):

    def __init(self):
        self.name = name
        self.requested_path = requested_path

    def backup(self):
        pass

    def sync(self):
        pass
        

def backup():
    '''Initiates a backup of the given path'''

    timestamp = '{:%Y-%m-%d %H-%M-%S}'.format(datetime.datetime.now())

    for dirName, subdirList, fileList in os.walk(requested_path):
        for file in fileList:
            file_path = os.path.join(dirName, file)

            try:
                remote_path = dirName.replace(requested_path, '')
                remote_path_correction = ''
                if remote_path != '':
                    remote_path_winfix = remote_path.replace('\\', '/') # stupid Windows...
                    remote_path_correction = remote_path_winfix.replace('//', '/')
                    remote_path_correction += '/'

                with open(file_path, mode='rb') as f:

                    # Ugly spaghetti fix for pathing issues caused by the Windows fix
                    if remote_path_correction == '':
                        pathfixer = '/'
                    else:
                        pathfixer = ''

                    dbx.files_upload(f.read(), path=f'/{name}/{timestamp}{pathfixer}{remote_path_correction}{file}')
                print(f"Uploaded '{name}': {file_path} at {timestamp}")

            except Exception as err:
                print(f'Failed to upload {file}, {err}')
                notifications.smtp(name, file_path, timestamp, err)

if __name__ == '__main__':
    backup()
