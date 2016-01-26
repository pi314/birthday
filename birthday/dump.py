from .model import Birthday


def command(args):
    Birthday.connect()
    for record in Birthday.select():
        print(record.name)
    Birthday.disconnect()
