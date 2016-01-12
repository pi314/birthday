import sqlite3
import os
import datetime

from .utils import captcha


HOME_DIR = os.path.expanduser("~")
DATABASE_FILE_NAME = '.birthday.sqlite'
DATABASE_FILE_PATH = os.path.join(HOME_DIR, DATABASE_FILE_NAME)
TABLE_NAME = 'Birthdays'


def connection_required(func):
    def wrapper(*args, **kwargs):
        if not Birthday.connection:
            raise Exception('Need database connection.')
        return func(*args, **kwargs)

    return wrapper


class Birthday:
    connection = None
    cursor = None

    @classmethod
    def connect(cls):
        if cls.connection: return

        try:
            cls.connection = sqlite3.connect(DATABASE_FILE_PATH)
            cls.cursor = cls.connection.cursor()
            cls.cursor.execute('''SELECT name FROM sqlite_master
                    WHERE type="table" AND name="{table_name}";'''.format(table_name=TABLE_NAME))
            if not cls.cursor.fetchone():
                cls.cursor.execute('''CREATE TABLE "{table_name}" (
                        "year" INTEGER DEFAULT 0,
                        "month" INTEGER DEFAULT 0,
                        "day" INTEGER DEFAULT 0,
                        "name" TEXT PRIMARY KEY DEFAULT "(empty)"
                        );'''.format(table_name=TABLE_NAME))
                cls.connection.commit()

        except sqlite3.DatabaseError as e:
            print('{} is corrupted, please remove it and try again.'.format(DATABASE_FILE_PATH))
            cls.connection.close()
            exit(1)

    @classmethod
    def disconnect(cls):
        if not cls.connection: return

        cls.connection.close()
        cls.connection = None
        cls.cursor = None

    @classmethod
    @connection_required
    def select(cls, constrains={}):
        today = datetime.date.today()

        for record in cls.cursor.execute('SELECT * FROM {TABLE_NAME} ORDER BY month, day, year, name;'.format(TABLE_NAME=TABLE_NAME)):
            record = Birthday(record[3], record[:3])
            if 'year' in constrains and record.year != constrains['year']:
                continue

            if 'month' in constrains and record.month != constrains['month']:
                continue

            if 'day' in constrains and record.day != constrains['day']:
                continue

            if 'name' in constrains and constrains['name'] not in record.name:
                continue

            if 'age' in constrains:
                if record.year == 0:
                    continue

                if today.year - record.year == constrains['age']:
                    if today.month < record.month:
                        continue

                    elif today.month > record.month:
                        yield record
                        continue

                    elif today.day < record.day:
                        continue

                    elif today.day >= record.day:
                        pass

                elif today.year - record.year == constrains['age'] + 1:
                    if today.month > record.month:
                        continue

                    elif today.month < record.month:
                        pass

                    elif today.day >= record.day:
                        continue

                    elif today.day < record.day:
                        pass

                else:
                    continue

            if 'next' in constrains:
                d1 = (datetime.date(today.year, record.month, record.day) - today).days
                d2 = (datetime.date(today.year + 1, record.month, record.day) - today).days

                if d1 >= 0 and d1 <= constrains['next']:
                    pass

                elif d2 >= 0 and d2 <= constrains['next']:
                    pass

                else:
                    continue

            yield record

    def __init__(self, name, date):
        self.year = date[0]
        self.month = date[1]
        self.day = date[2]
        self.name = name

    def __str__(self):
        return '{:>04}/{:>02}/{:>02} {}'.format(
            self.year if self.year else '----',
            self.month if self.month else '--',
            self.day if self.day else '--',
            self.name
        )

    @connection_required
    def write(self):
        if self.exists():
            return False

        self.cursor.execute('''INSERT INTO {TABLE_NAME}
            (name, year, month, day)
            VALUES ("{name}", {year}, {month}, {day});'''.format(
            year=self.year,
            month=self.month,
            day=self.day,
            name=self.name,
            TABLE_NAME=TABLE_NAME)
        )
        self.connection.commit()
        return True

    @connection_required
    def exists(self):
        self.cursor.execute('''SELECT * FROM {TABLE_NAME} WHERE name='{name}'
            '''.format(name=self.name, TABLE_NAME=TABLE_NAME))

        return self.cursor.fetchone() is not None

    @connection_required
    @captcha
    def override(self):
        if not self.exists(): return

        self.cursor.execute('''UPDATE {TABLE_NAME}
                SET year={year},
                month={month},
                day={day} WHERE name='{name}';'''.format(
            year=self.year,
            month=self.month,
            day=self.day,
            name=self.name,
            TABLE_NAME=TABLE_NAME)
        )
        self.connection.commit()
        print('Record [{new_record}] had been updated into database.'.format(
            new_record=self,
            DATABASE_FILE=DATABASE_FILE_PATH,))

    def diff(self, another):
        return '[{}/{}/{}] -> [{}/{}/{}]'.format(
            self.diff_a(4, self.year, another.year),
            self.diff_a(2, self.month, another.month),
            self.diff_a(2, self.day, another.day),
            self.diff_b(4, self.year, another.year),
            self.diff_b(2, self.month, another.month),
            self.diff_b(2, self.day, another.day),
        )

    def diff_a(self, width, va, vb):
        if va == 0 and vb != 0:
            c1, c2 = ('\033[1;32m', '\033[m')
        elif va == 0 or vb == 0 or va == vb:
            c1, c2 = ('', '')
        else:
            c1, c2 = ('\033[1;33m', '\033[m')

        return '{c1}{value:{fill}>{width}}{c2}'.format(
            c1=c1, c2=c2,
            value=va if va else '-',
            fill='0' if va else '-',
            width=width,
        )

    def diff_b(self, width, va, vb):
        if va == 0 and vb != 0:
            c1, c2, v = ('\033[1;32m', '\033[m', vb)
        elif va == 0 or vb == 0 or va == vb:
            c1, c2, v = ('', '', va)
        else:
            c1, c2, v = ('\033[1;33m', '\033[m', vb)

        return '{c1}{value:{fill}>{width}}{c2}'.format(
            c1=c1, c2=c2,
            value=v if v else '-',
            fill='0' if v else '-',
            width=width,
        )

    def __add__(self, another):
        ret = Birthday(self.name, [self.year, self.month, self.day])
        if self.name != another.name:
            raise ValueError('Cannot add two records with different name.')

        if another.year != 0:
            ret.year = another.year

        if another.month != 0:
            ret.month = another.month

        if another.day != 0:
            ret.day = another.day

        return ret

    def __le__(self, another):
        if self.name != another.name:
            raise ValueError('Cannot compare two records with different name.')

        return (self.year == 0 or self.year == another.year) and\
            (self.month == 0 or self.month == another.month) and\
            (self.day == 0 or self.day == another.day)

    def __eq__(self, another):
        return (self.name == another.name and
            self.year == another.year and
            self.month == another.month and
            self.day == another.day)
