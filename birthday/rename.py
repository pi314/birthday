from .model import Birthday
from .utils import captcha


def command(args):
    Birthday.connect()
    try:
        target_birthday = next(Birthday.select({'name': args.old_name}))
        print('Rename [{}] to [{}]?'.format(target_birthday.name, args.new_name))
        captcha()
        target_birthday.delete()
        target_birthday.name = args.new_name
        target_birthday.write()
        print('Record [{}] renamed.'.format(target_birthday))

    except StopIteration:
        print('[{}] does not exist.'.format(args.old_name))
    Birthday.disconnect()
