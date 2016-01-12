from .model import Birthday

def command(args):
    Birthday.connect()
    try:
        target_birthday = next(Birthday.select({'name': args.name}))
        print('Delete [{}]?'.format(target_birthday))
        target_birthday.delete()
        print('Record [{}] deleted.'.format(target_birthday))

    except StopIteration:
        print('[{}] does not exist.'.format(args.name))

    Birthday.disconnect()
