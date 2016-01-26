from .model import Birthday


def command(args):
    Birthday.connect()
    if args.info == 'names':
        for record in Birthday.select():
            print(record.name)

    elif args.info == 'years':
        for record in Birthday.select():
            if record.year:
                print(record.year)

    Birthday.disconnect()
