import smtplib

import config


def smtp(name, file_path, timestamp, err):
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
        print('Notification sent.')

    except:
        print('Failed to send notification.')
        exit(1)