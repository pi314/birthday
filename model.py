import sqlite3
import os

from utils import captcha


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
    def all(cls):
        for record in cls.cursor.execute('SELECT * FROM {TABLE_NAME};'.format(TABLE_NAME=TABLE_NAME)):
            yield Birthday(record[3], record[:3])

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
            # record with same name exists
            print('Record name [{}] exists.'.format(self.name))
            self.cursor.execute('''SELECT * FROM {TABLE_NAME} WHERE name='{name}'
                '''.format(name=self.name, TABLE_NAME=TABLE_NAME))

            old = self.cursor.fetchone()
            old = Birthday(old[3], old[:3])

            if self != old:
                print('Override? [{}] -> [{}]'.format(self - old, old - self))
                self.override()

            return

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
        print('Record [{new_record}] had been added into database.'.format(
            new_record=self,
            DATABASE_FILE=DATABASE_FILE_PATH,))

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

    def __sub__(self, another):
        return BirthdayDiff(self, another)

    def __eq__(self, another):
        return (self.name == another.name and
            self.year == another.year and
            self.month == another.month and
            self.day == another.day)


class BirthdayDiff:
    def __init__(self, a, b):
        self.a = [a.year, a.month, a.day]
        self.b = [b.year, b.month, b.day]

    def __str__(self):
        return '{}/{}/{}'.format(
            self.color(4, 0),
            self.color(2, 1),
            self.color(2, 2),
        )

    def color(self, width, index):
        if self.a[index] == self.b[index]:
            c1 = ''
            c2 = ''
        else:
            c1 = '\033[1;33m'
            c2 = '\033[m'

        return '{c1}{value:{fill}>{width}}{c2}'.format(
            c1=c1, c2=c2,
            value=self.b[index] if self.b[index] else '-',
            fill='0' if self.b[index] else '-',
            width=width,
        )
