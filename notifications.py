import smtplib

import config

def smtp(msg):
    # Istantiate smtplib & log in if needed 
    # SMTP_SSL is used here -- allow configuration for insecure SMTP servers later?
    try: 
        notify = smtplib.SMTP_SSL(host=config.smtp_host, port=config.smtp_port)
        if config.smtp_auth_req == 1:
            notify.login(config.smtp_username, config.smtp_password)
        notify.sendmail(config.smtp_sendfrom, config.smtp_sendto, msg)
        print('Notification sent.')

    except:
        print('Failed to send notification.')
        exit(1)


def smtp_error(name, file_path, timestamp, err):
    ''' Sends an email notification when the backup fails with an error.'''

    # Find a way to make this message work correctly if appropriate spacing is added. It's ugly.
    error_notification =  f"""From: DirectoryBackup <{config.smtp_sendfrom}>
To: DirBak User <{config.smtp_sendto}>
Subject: DirBak Job {name} failed

Backup of "{file_path}" failed at {timestamp}

Error message: {err}"""

    smtp(error_notification)


def smtp_generic(msg):
    ''' Sends an email notification with any generic message '''

    msg =  f"""From: DirectoryBackup <{config.smtp_sendfrom}>
To: DirBak User <{config.smtp_sendto}>
Subject: DirBak Notification

{msg}"""

    smtp(msg)
