import re
import argparse
import datetime

from .model import Birthday
from .utils import captcha


def command(args):
    Birthday.connect()
    new_birthday = Birthday(name=args.name, date=args.date)
    if not new_birthday.exists():
        new_birthday.write()
        print('Record [{new_record}] had been added into database.'.format(
            new_record=new_birthday)
        )
    else:
        old = next(Birthday.select({'name': args.name}))
        new = old + new_birthday
        if new != old:
            print('Record name [{}] exists.'.format(old.name))
            print('{}? {}'.format(
                'Merge' if old <= new else 'Override',
                old.diff(new)
            ))
            captcha()
            new.override()
        else:
            print('Record [{}] not changed.'.format(old.name))

    Birthday.disconnect()


def raise_format_error():
    raise argparse.ArgumentTypeError('Date should be in format:\n'
        '    <date>:  <year>/<month>/<day> | <year>/today | today\n'
        '    <year>:  xxxx | \d\d\d\d\n'
        '    <month>: xx | \d\d\n'
        '    <day>:   xx | \d\d')


def date_str(s: str):
    m = re.match(r'^(?:(\d{4}|xxxx)/)?(?:(\d\d|xx)/(\d\d|xx)|(today))$', s)
    if not m:
        raise_format_error()

    try:
        yy = 0 if m.group(1) == 'xxxx' else int(m.group(1))

        if m.group(4):
            today = datetime.date.today()
            mm = today.month
            dd = today.day

        else:
            mm = 0 if m.group(2) == 'xx' else int(m.group(2))
            dd = 0 if m.group(3) == 'xx' else int(m.group(3))

    except ValueError:
        raise_format_error()

    if (yy, mm, dd) == (0, 0, 0):
        raise argparse.ArgumentTypeError('Date cannot be totally unknown.')


    return [yy, mm, dd]
