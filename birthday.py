#!/usr/bin/env python
import argparse
import sqlite3
import sys
from os.path import expanduser

HOME_DIR = expanduser("~")
DATABASE_FILE_NAME = '.birthday.sqlite'
DATABASE_FILE_PATH = '{}/{}'.format(HOME_DIR, DATABASE_FILE_NAME)
TABLE_NAME = 'Birthdays'
CAPTCHA_LENGTH = 3


class BirthdayRecord:
    def __init__(self, name, year=0, month=0, day=0, ignore=0):
        self.year = year
        self.month = month
        self.day = day
        self.name = name
        self.ignore = ignore

    def __str__(self):
        return '[{year}/{month}/{day} {name}]'.format(
                year=self.q4(self.year),
                month=self.q2(self.month),
                day=self.q2(self.day),
                name=self.name
            )

    # question marks
    def q(self, value, width):
        if value == 0:
            return '?' * width

        return '{:0>2}'.format(value)

    def q4(self, value):
        return self.q(value, 4)

    def q2(self, value):
        return self.q(value, 2)

    # colored question marks
    def cq4(self, value1, value2):
        qs = self.q4(value1)
        if value1 == value2:
            return qs
        return '\033[1;33m{}\033[m'.format(qs)

    # colored question marks
    def cq2(self, value1, value2):
        qs = self.q2(value1)
        if value1 == value2:
            return qs
        return '\033[1;33m{}\033[m'.format(qs)

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

    def diff(self, another_record):
        if not isinstance(another_record, BirthdayRecord):
            return str(self)

        return '[{year}/{month}/{day} {name}]'.format(
                year=self.cq4(self.year, another_record.year),
                month=self.cq2(self.month, another_record.month),
                day=self.cq2(self.day, another_record.day),
                name=self.name
            )


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


def _gen_captcha():
    import random
    import string
    return ''.join(random.sample(string.ascii_lowercase + string.digits, CAPTCHA_LENGTH))


def _ask_user_to_replace(old_record, new_record):
    while True:
        captcha = _gen_captcha()
        print('Update record: {old_record} -> {new_record}'.format(
            old_record=old_record.diff(new_record),
            new_record=new_record.diff(old_record),
            file=sys.stderr))
        print('Input captcha to confirm, or Ctrl-C to cancel [{}]:'.format(captcha), end=' ')
        if input().strip() == captcha:
            return True

        print('Captcha incorrect.')
        print()


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
            return

        _ask_user_to_replace(old_record, new_record)
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
