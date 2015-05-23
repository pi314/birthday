#!/usr/bin/env python
import argparse
import sqlite3
import sys
from os.path import expanduser

HOME_DIR = expanduser("~")
DATABASE_FILE_NAME = '.birthday.sqlite'
DATABASE_FILE_PATH = '{}/{}'.format(HOME_DIR, DATABASE_FILE_NAME)
TABLE_NAME = 'Birthdays'


class BirthdayRecord:
    def __init__(self, name, year=0, month=0, day=0, ignore=0):
        self.year = year
        self.month = month
        self.day = day
        self.name = name
        self.ignore = ignore

    def __str__(self):
        return '[{}/{}/{} {}]'.format(
                self.q4(self.year),
                self.q2(self.month),
                self.q2(self.day),
                self.name
            )

    def q(self, value, width):
        if value == 0:
            return '?' * width

        return '{:0>2}'.format(value)

    def q4(self, value):
        return self.q(value, 4)

    def q2(self, value):
        return self.q(value, 2)

    def copy(self):
        return BirthdayRecord(self.name, year=self.year, month=self.month, day=self.day, ignore=self.ignore)

    def update(self, another_record):
        if not isinstance(another_record, BirthdayRecord):
            return

        if another_record.year != 0:
            self.year = another_record.year

        if another_record.month != 0:
            self.month = another_record.month

        if another_record.day != 0:
            self.day = another_record.day

    @property
    def update_sql(self):
        return 'UPDATE {table_name} SET year={year}, month={month}, day={day} WHERE name=\'{name}\';'.format(
            year=self.year,
            month=self.month,
            day=self.day,
            name=self.name,
            table_name=TABLE_NAME,)

    @property
    def insert_sql(self):
        return '''INSERT INTO {table_name}
            (id, name, year, month, day)
            VALUES (NULL, "{name}", {year}, {month}, {day});'''.format(
                year=self.year,
                month=self.month,
                day=self.day,
                name=self.name,
                table_name=TABLE_NAME,)

    def __eq__(self, another_record):
        if not isinstance(another_record, BirthdayRecord):
            return False

        return self.name == another_record.name and \
               self.year == another_record.year and \
               self.month == another_record.month and \
               self.day == another_record.day


def _check_db():
    try:
        conn = sqlite3.connect(DATABASE_FILE_PATH)
        cur = conn.cursor()
        cur.execute('''SELECT name FROM sqlite_master
            WHERE type="table" AND name="{table_name}";'''.format(table_name=TABLE_NAME))
        if cur.fetchone() is None:
            cur.execute('''CREATE TABLE "{table_name}" (
                "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                "year" INTEGER DEFAULT 0,
                "month" INTEGER DEFAULT 0,
                "day" INTEGER DEFAULT 0,
                "name" TEXT DEFAULT "(empty)",
                "ignore" INTEGER DEFAULT 0
                );'''.format(table_name=TABLE_NAME))
            conn.commit()

        return conn

    except sqlite3.DatabaseError as e:
        print('{} is corrupted, please remove it and try again.'.format(DATABASE_FILE_PATH),
            file=sys.stderr)
        conn.close()
        exit(1)


def _find_existed_record(cur, name):
    # single quote needed here, double quote means **identifier** in sqlite
    cur.execute("SELECT id,year,month,day,name FROM {table_name} WHERE name='{name}';".format(
        table_name=TABLE_NAME, name=name))
    old_record = cur.fetchone()
    if old_record is None:
        return None

    year = old_record[1]
    month = old_record[2]
    day = old_record[3]
    name = old_record[4]
    return BirthdayRecord(name, year=year, month=month, day=day)


def _ask_user_to_replace(old_record, new_record):
    choice = None
    while not isinstance(choice, bool):
        print('{old_record} exists in database, replace with {new_record}? [Y/n]'.format(
            old_record=old_record,
            new_record=new_record,
            file=sys.stderr), end=' ')
        choice = {'': True, 'y': True, 'yes': True, 'n': False, 'no': False}.get(input().strip().lower(), None)

    return choice


def _insert_new_record(conn, new_record):
    cur = conn.cursor()
    cur.execute(new_record.insert_sql)
    conn.commit()
    print('{new_record} added into database {database_file}'.format(
        new_record=new_record,
        database_file=DATABASE_FILE_PATH,))


def add_operation(args):
    if not any((args.year, args.month, args.day)):
        args.parser.error('At least one of { year | month | day } needed.')
    input_record = BirthdayRecord(args.name, year=args.year, month=args.month, day=args.day)

    conn = _check_db()
    cur = conn.cursor()
    old_record = _find_existed_record(cur, args.name)

    if old_record is not None:
        new_record = old_record.copy()
        new_record.update(input_record)
        if new_record == old_record:
            print('{old_record} not changed'.format(old_record=old_record))

        elif _ask_user_to_replace(old_record, new_record) == True:
            cur.execute(new_record.update_sql)
            conn.commit()
            print('{new_record} updated into database {database_file}'.format(
                new_record=new_record,
                database_file=DATABASE_FILE_PATH,))

    else:
        _insert_new_record(conn=conn, new_record=input_record)


def show_operation(args):
    print('show', args)


def main():
    top_parser = argparse.ArgumentParser(description='''Manage birthday date of your friends''')
    subparsers = top_parser.add_subparsers(description='valid subcommands', dest='subparser_name')

    parser_add = subparsers.add_parser('add', help='add records')
    parser_add.add_argument('-y', '--year', type=int, default=0)
    parser_add.add_argument('-m', '--month', type=int, default=0)
    parser_add.add_argument('-d', '--day', type=int, default=0)
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
