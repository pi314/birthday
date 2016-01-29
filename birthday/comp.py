from .utils import color_code
from .model import Birthday


def command(args):
    Birthday.connect()
    if args.info[0] == 'names':
        for record in Birthday.select():
            print(record.name)

    elif args.info[0] == 'year-of':
        try:
            target = next(Birthday.select({'name': args.info[1]}))
            print('{:>04}'.format(target.year if target.year else 'xxxx'))
        except StopIteration:
            print('xxxx')

    elif args.info[0] == 'month-of':
        try:
            target = next(Birthday.select({'name': args.info[1]}))
            print('{:>02}'.format(target.month if target.month else 'xx'))
        except StopIteration:
            print('xx')

    elif args.info[0] == 'day-of':
        try:
            target = next(Birthday.select({'name': args.info[1]}))
            print('{:>02}'.format(target.day if target.day else 'xx'))
        except StopIteration:
            print('xx')

    elif args.info[0] == 'colors':
        for color in color_code:
            print(color)

    Birthday.disconnect()
