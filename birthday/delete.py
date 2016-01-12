from .model import Birthday
from .utils import captcha

def command(args):
    Birthday.connect()
    try:
        target_birthday = next(Birthday.select({'name': args.name}))
        print('Delete [{}]?'.format(target_birthday))
        captcha()
        target_birthday.delete()
        print('Record [{}] deleted.'.format(target_birthday))

    except StopIteration:
        print('[{}] does not exist.'.format(args.name))

    Birthday.disconnect()
