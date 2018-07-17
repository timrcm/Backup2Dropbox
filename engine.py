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
        
        self.dbx = db.Dropbox(config.dbxAccount)

        self.target = target
        self.style = style
        self.name = name
        self.requested_path = requested_path
        self.timestamp = timestamp()
        self.error_count = 0
        self.error_log = open('errors.log', 'w')

        if self.style == "backup":
            self.backup()
        elif self.style == "sync":
            self.sync()
        else:
            self.err = f"Unknown backup style for target {target}."
            notifications.smtp_error(self.name, self.requested_path, self.timestamp, self.err)

        self.error_log.close()
        self.completed()


    def __call__(self):
        pass

    def backup(self):
        '''Initiates a backup of the given path to Dropbox'''

        for dirpath, dirnames, filenames in os.walk(self.requested_path):
            for file in filenames:
                self.file_path = os.path.join(dirpath, file)

                try:
                    # Cut out all preceding directories from the remote path
                    self.remote_path = dirpath.replace(self.requested_path, '')

                    with open(self.file_path, mode='rb') as f:
                        # Path the files will live in on Dropbox
                        # os.path.join works just fine on a *nix box, but Windows causes issues... 
                        self.dbpath = f'/{self.name}/{self.timestamp}/{self.remote_path}/{file}'
                        self.dbpath = self.dbpath.replace('\\', '/') # Fix for Windows' silly nonsense 
                        self.dbpath = self.dbpath.replace('//', '/') # Fix for duplicates caused by the above
                        
                        # Check if the file is greater than chunk_size in config.py. If so, upload it in chunks.
                        file_size = os.path.getsize(self.file_path)

                        if file_size <= config.chunk_size:
                            self.dbx.files_upload(f.read(), path=self.dbpath)
                        else:
                            self.bigupload(f, file_size)   

                    # Once the 'try' statement finishes successfully, print that success 
                    print(f"Uploaded '{self.name}': {self.file_path} at {self.timestamp}")

                # Print a notification & append the error to the log if something failed 
                except Exception as err:
                    self.error_count += 1
                    print(f'Failed to upload {file}, {err}')
                    self.error_log.write(f'Error uploading {self.file_path}: {err}\n\n')

        if config.cleanup == 1:
            self.cleanup()


    def bigupload(self, f, file_size):
        '''Handles uploads that must be done in chunks due to being larger than 50MB'''

        # Start an upload session to Dropbox
        session_start = self.dbx.files_upload_session_start(f.read(config.chunk_size))
        # Keep track of the session and what byte we're at in the upload process
        cursor = db.files.UploadSessionCursor(session_id=session_start.session_id, offset=f.tell())
        # Where the uploaded file will go when the session closes
        commit = db.files.CommitInfo(path=self.dbpath)

        # Continue until no bytes remain in file_size
        while f.tell() < file_size:
            # If the file size is LESS than the configured chunk size, finish the upload session
            if ((file_size - f.tell()) <= config.chunk_size):
                self.dbx.files_upload_session_finish(f.read(config.chunk_size), cursor, commit)

            # If the file is not less than the configured chunk size, append another chunk
            # to the file & update the cursor position
            else: 
                self.dbx.files_upload_session_append_v2(f.read(config.chunk_size), cursor, close=False)
                cursor.offset = f.tell()


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
            self.error_log.write(f'Sync job failed to clean up previous job(s) with the error: {err}.\n\n')
            self.backup()


    def cleanup(self):
        '''Not yet functional. Cleans up the backup set based on the configured number of sets to keep.'''
        x = self.dbx.files_list_folder(f'/{self.name}')
        print(x)


    def completed(self):
        '''Checks if notifications upon completion are enabled, sending one if so.'''
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
        self.error_count = 0

    def __call__(self):
        pass

    def backup(self):
        pass

    def sync(self):
        pass

    def cleanup(self):
        pass
