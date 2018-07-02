# DirBak
# Takes an environment path and backs it up to Dropbox
# 7/1/2018 TimRCM

import datetime
import os
import smtplib
from sys import argv

import dropbox

import config

script, name, requested_path = argv
dbx = dropbox.Dropbox(config.dbxAccount)


def backup():
    '''Initiates a backup of the given path'''

    timestamp = '{:%Y-%m-%d %H-%M-%S}'.format(datetime.datetime.now())

    for dirName, subdirList, fileList in os.walk(requested_path):
        for file in fileList:
            file_path = os.path.join(dirName, file)

            try:
                remote_path = dirName.replace(f"{requested_path}", '')
                remote_path_correction = ''
                if remote_path != '':
                    remote_path_winfix = remote_path.replace('\\', '/') # stupid fucking Windows
                    remote_path_correction = remote_path_winfix.replace('//', '/')
                    remote_path_correction += '/'

                with open(f'{file_path}', mode='rb') as f:

                    # Ugly spaghetti fix for pathing issues caused by the Windows fix
                    if remote_path_correction == '':
                        pathfixer = '/'
                    else:
                        pathfixer = ''

                    dbx.files_upload(f.read(), path=f'/{name}/{timestamp}{pathfixer}{remote_path_correction}{file}')
                print(f"Uploaded '{name}': {file_path} at {timestamp}")

            except Exception as err:
                print(f"Failed to upload {file}, {err}")
                notification(file_path, timestamp, err)


def notification(file_path, timestamp, err):
    ''' Sends an email notification when the backup fails for any reason.'''

    failure_notification =  f"""From: DirectoryBackup <{config.smtp_sendfrom}>
To: DirBak User <{config.smtp_sendto}>
Subject: DirBak Job {name} failed

Backup of "{file_path}" failed at {timestamp}

Error message: {err}"""

    # Istantiate smtplib & log in if needed 
    # SMTP_SSL is used here -- allow configuration for insecure SMTP servers later?
    try: 
        notify = smtplib.SMTP_SSL(host=config.smtp_host, port=config.smtp_port)
        if config.smtp_auth_req == 1:
            notify.login(config.smtp_username, config.smtp_password)
        notify.sendmail(config.smtp_sendfrom, config.smtp_sendto, failure_notification)
        print("Notification sent.")

    except:
        print("Failed to send notification.")
        exit(1)
    

if __name__ == '__main__':
    backup()
