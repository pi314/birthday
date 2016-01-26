#!/usr/bin/env python
import argparse
import sqlite3
import sys
import os
import re

from . import show
from . import add
from . import delete
from . import rename
from . import dump


def help_(args):
    if args.subcommand is None:
        args.top_parser.print_help()
        exit(1)

    if args.subcommand not in args.choices:
        args.top_parser.error('Invalid subcommand: {}'.format(args.subcommand))

    args.choices[args.subcommand].print_help()


def main():
    top_parser = argparse.ArgumentParser(
        prog='birthday',
        description='Manage birthdays of your friends.',
        add_help=False,
        formatter_class=argparse.RawTextHelpFormatter)
    subparsers = top_parser.add_subparsers(
        title='Available subcommands',
        metavar='<subcommand>')

    parser_help = subparsers.add_parser('help',
        help='Usage of subcommands',
        add_help=False)
    parser_help.add_argument('subcommand',
        type=str, nargs='?',
        help='Subcommand'
    )
    parser_help.set_defaults(func=help_)
    parser_help.set_defaults(top_parser=top_parser)
    parser_help.set_defaults(choices=subparsers.choices)

    # birthday show
    parser_show = subparsers.add_parser('show',
        help='Show records with filtering constrains',
        add_help=False)
    parser_show.add_argument('constrains',
        type=show.constrain_str,
        nargs='*', help='''In format "constrain=value".
            Available constrains: year, age, month, day, name, next''')
    parser_show.add_argument('-c', '--color', dest='highlight_today',
        type=show.color_str,
        help='Highlight today')
    parser_show.set_defaults(func=show.command)

    # birthday add
    parser_add = subparsers.add_parser('add',
        help='Add new record with partial informations',
        add_help=False)
    parser_add.add_argument('name', type=str, help='the name of your friend')
    parser_add.add_argument('date', type=add.date_str,
        help='the birthday of your friend, in xxxx/xx/xx format')
    parser_add.set_defaults(func=add.command)

    # birthday delete
    parser_delete = subparsers.add_parser('delete',
        help='Remove record by name',
        add_help=False)
    parser_delete.add_argument('name', type=str, help='the name of record')
    parser_delete.set_defaults(func=delete.command)

    # birthday rename
    parser_rename = subparsers.add_parser('rename',
        help='Rename record by name',
        add_help=False)
    parser_rename.add_argument('old_name', type=str, help='the old name of your friend')
    parser_rename.add_argument('new_name', type=str, help='the new name of your friend')
    parser_rename.set_defaults(func=rename.command)

    # birthday dump  ### for shell completion ###
    parser_completion = subparsers.add_parser('dump', add_help=False)
    parser_completion.add_argument('info', type=str, help='{names}')
    parser_completion.set_defaults(func=dump.command)

    try:
        args = top_parser.parse_args()
        if not hasattr(args, 'func'):
            top_parser.print_help()
            exit(1)

        args.func(args)
    except KeyboardInterrupt:
        exit(1)


if __name__ == '__main__':
    main()
