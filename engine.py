# DirBak
# Takes an environment path and backs it up to Dropbox
# 7/1/2018 TimRCM

import datetime
import os
from sys import argv

import config
import notifications

script, target, style, name, requested_path = argv


def timestamp():
    '''Generates the current timestamp based on system time'''
    return '{:%Y-%m-%d %H-%M-%S}'.format(datetime.datetime.now())

def datestamp():
    '''Generates the current datestamp based on system time
    Not currently in use - this may be useful to do basic math on for determining 
    backup set age for APIs that won't hand over that information'''
    return '{:%Y%m%d}'.format(datetime.datetime.now())

class dropbox(object):
    '''Utilizes the Dropbox API to performs a backup or sync of a given directory'''

    def __init__(self):
        import dropbox as db
        self.dbx = db.Dropbox(config.dbxAccount)

        self.target = target
        self.style = style
        self.name = name
        self.requested_path = requested_path
        self.timestamp = timestamp()
        self.error_count = 0

        if self.style == "backup":
            self.backup()
        elif self.style == "sync":
            self.sync()
        else:
            self.err = f"Unknown backup style for target {target}."
            notifications.smtp_error(self.name, self.requested_path, self.timestamp, self.err)

        self.completed()


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
                        self.dbx.files_upload(f.read(), path=f'/{self.name}/{self.timestamp}{self.pathfixer}{self.remote_path_correction}{file}')
                    
                    print(f"Uploaded '{self.name}': {self.file_path} at {self.timestamp}")

                # Send a notification if something failed 
                except Exception as err:
                    self.error_count += 1
                    print(f'Failed to upload {file}, {err}')
                    notifications.smtp_error(self.name, self.file_path, self.timestamp, err)

        if config.cleanup == 1:
            self.cleanup()


    def sync(self):
        '''Until I find a cleaner way... this method deletes the old backup set, and then adds a fresh one.
        This is fairly safe to do with Dropbox's built-in file versioning. There does not appear to be a 
        native method to do this less destructively with Dropbox's API.'''

        try:
            self.dbx.files_delete(f'/{self.name}')
            self.backup()
        except Exception as err:
            self.error_count += 1
            print(f'Cleanup of {name} failed with the error: {err}.')
            notifications.smtp_generic(f'''Sync job failed to clean up previous job(s) with the error {err}. \nProceeded with fresh backup set anyway - please verify.''')
            self.backup()


    def cleanup(self):
        '''Not yet functional. Cleans up the backup set based on the configured number of sets to keep.'''
        x = self.dbx.files_list_folder(f'/{self.name}')
        print(x)


    def completed(self):
        print(f"DirBak job '{self.name} {self.style}' completed.")
        if config.smtp_notify_after_completion == 1:
            self.end_time = timestamp()
            # self.space_remaining = self.dbx.users_get_space_usage()
            notifications.smtp_completed(self.name, self.style, self.error_count, self.timestamp, self.end_time)



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
