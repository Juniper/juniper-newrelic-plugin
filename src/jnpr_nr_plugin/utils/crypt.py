import base64
import getpass
import zlib


def main():
    prompt = True
    while prompt:
        pwd = getpass.getpass('enter password: ')
        print 'encode password ' + base64.b64encode(zlib.compress(pwd, 9))
        usr_opt = raw_input('enter more? yes|no')
        if usr_opt == 'yes':
            continue
        else:
            prompt = False


if __name__ == '__main__':
    main()
