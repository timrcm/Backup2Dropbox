import smtplib

import config

headers = f"""From: DirectoryBackup <{config.smtp_sendfrom}>
To: DirBak User <{config.smtp_sendto}>
Subject: DirBak Notification
"""

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
    '''Sends an email notification when the backup fails with an error.'''
    msg =  f"""{headers}
    Backup of "{file_path}" failed at {timestamp}
    Error message: {err}"""
    smtp(msg)


def smtp_completed(name, style, error_count, start_time, end_time):
    error_log = open('errors.log', 'r')
    '''Sends an email notification on completion of a job'''
    msg =  f"""{headers}
    DirBak job '{name} {style}' started at {start_time} & completed at {end_time} with {error_count} error(s).
    
    Errors encountered (if any): 
    
    {error_log.read()}"""
    smtp(msg)


def smtp_generic(msg):
    '''Sends an email notification with any generic message'''
    msg =  f"""{headers}
    {msg}"""
    smtp(msg)