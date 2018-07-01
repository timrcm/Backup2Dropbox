# Backup2Dropbox
# Takes an environment path and backs it up to Dropbox
# 7/1/2018 TimRCM

from sys import argv
import datetime
import smtplib

import dropbox 

import config 

path = argv

dbx = dropbox.Dropbox(config.dbxAccount)
dbx.users_get_current_account()
print(dbx.users_get_current_account())


def backup():
    pass

def notification():
    ''' Sends an email notification when the backup fails for any reason.'''

    message = f"""From: DirectoryBackup <{config.smtp_sendfrom}>
        To: <{config.smtp_sendto}>
        Subject: SMTP e-mail test

        This is a test e-mail notification.

    """

    # Istantiate smtplib & log in if needed 
    # SMTP_SSL is used here -- allow configuration for insecure SMTP servers later?
    try: 
        notify = smtplib.SMTP_SSL(host=config.smtp_host, port=config.smtp_port)
        if config.smtp_auth_req == 1:
            notify.login(config.smtp_username, config.smtp_password)
        notify.sendmail(config.smtp_sendfrom, config.smtp_sendto, message)
        print("Message sent... maybe.")

    except:
        print("Failed to send message.")
        exit(1)
    
if __name__ == '__main__':
    notification()
