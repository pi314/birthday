#!/usr/bin/env python
import argparse


def add_operation(args):
    if not any((args.year, args.month, args.day)):
        args.parser.error('At least one of { year | month | day } needed.')
    print('add', args)


def show_operation(args):
    print('show', args)


def main():
    top_parser = argparse.ArgumentParser(description='''Manage birthday date of your friends''')
    subparsers = top_parser.add_subparsers(description='valid subcommands', dest='subparser_name')

    parser_add = subparsers.add_parser('add', help='add records')
    parser_add.add_argument('-y', '--year', type=int)
    parser_add.add_argument('-m', '--month', type=int)
    parser_add.add_argument('-d', '--day', type=int)
    parser_add.add_argument('name', type=str)
    parser_add.set_defaults(func=add_operation)
    parser_add.set_defaults(parser=parser_add)

    parser_show = subparsers.add_parser('show', help='show records')
    parser_show.add_argument('-y', '--year', type=int)
    parser_show.add_argument('-m', '--month', type=int)
    parser_show.add_argument('-d', '--day', type=int)
    parser_show.add_argument('-n', '--name', type=str)
    parser_show.add_argument('-a', '--all', action='store_true')
    parser_show.add_argument('-u', '--upcoming-days', type=int)
    parser_show.set_defaults(func=show_operation)
    parser_show.set_defaults(parser=parser_show)

    args = top_parser.parse_args()
    if not hasattr(args, 'func'):
        top_parser.print_help()
        exit(1)

    args.func(args)


if __name__ == '__main__':
    main()
