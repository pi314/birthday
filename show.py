import argparse

from model import Birthday


def command(args):
    Birthday.connect()
    constrains = args.constrains
    for r in Birthday.all():
        print(r)

    print('constrains:', constrains)
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
            raise argparse.ArgumentTypeError('Constrain {} error: value should be an integer.'.format(p[0]))

    elif p[0] in ('name',):
        pass

    else:
        raise argparse.ArgumentTypeError('Unknown constrain: {}.'.format(p[0]))

    return p
