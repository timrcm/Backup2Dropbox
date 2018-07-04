import engine
import notifications

if __name__ == '__main__':
    if engine.target == 'dropbox':
        engine.dropbox()
    elif engine.target == 'b2': 
        engine.b2()
    else:
        print("Invalid target specified.")
        notifications.smtp_generic("DirBak job did not run - invalid target specified.")
        exit(1)
