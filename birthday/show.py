import argparse

from .model import Birthday


def command(args):
    Birthday.connect()
    constrains = dict(args.constrains)

    if 'age' in constrains and 'year' in constrains:
        raise argparse.ArgumentError('Constrain error: "year" cannot be used with "age".')

    for record in Birthday.select(constrains):
        print(record)

    Birthday.disconnect()


def constrain_str(s: str):
    p = s.split('=')
    if len(p) != 2:
        raise argparse.ArgumentTypeError('Constrains should be in "key=value" format.')

    if p[0] in ('year', 'age', 'month', 'day', 'next'):
        try:
            p[1] = int(p[1])
            if p[0] in ('age', 'month', 'day') and p[1] <= 0:
                raise argparse.ArgumentTypeError('Constrain {} error: value should larger than zero.'.format(p[0]))

        except ValueError:
            month_name_list = [
                'January', 'February', 'March',
                'April', 'May', 'June',
                'July', 'August', 'September',
                'October', 'November', 'December',
                'Jan', 'Feb', 'Mar',
                'Apr', 'May', 'Jun',
                'Jul', 'Aug', 'Sep',
                'Oct', 'Nov', 'Dec',
                ]
            if p[0] == 'month' and p[1] in month_name_list:
                p[1] = (month_name_list.index(p[1]) % 12) + 1

            else:
                raise argparse.ArgumentTypeError('Constrain {} error: value should be an integer.'.format(p[0]))

    elif p[0] in ('name',):
        pass

    else:
        raise argparse.ArgumentTypeError('Unknown constrain: {}.'.format(p[0]))

    return p
