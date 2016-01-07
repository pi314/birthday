import sqlite3
import os


HOME_DIR = os.path.expanduser("~")
DATABASE_FILE_NAME = '.birthday.sqlite'
DATABASE_FILE_PATH = os.path.join(HOME_DIR, DATABASE_FILE_NAME)
TABLE_NAME = 'Birthdays'


class Birthday:
    conn = None

    @classmethod
    def connect(cls):
        if cls.conn: return

        try:
            cls.conn = sqlite3.connect(DATABASE_FILE_PATH)
            cur = cls.conn.cursor()
            cur.execute('''SELECT name FROM sqlite_master
                    WHERE type="table" AND name="{table_name}";'''.format(table_name=TABLE_NAME))
            if not cur.fetchone():
                cur.execute('''CREATE TABLE "{table_name}" (
                        "year" INTEGER DEFAULT 0,
                        "month" INTEGER DEFAULT 0,
                        "day" INTEGER DEFAULT 0,
                        "name" TEXT PRIMARY KEY DEFAULT "(empty)"
                        );'''.format(table_name=TABLE_NAME))
                cls.conn.commit()

        except sqlite3.DatabaseError as e:
            print('{} is corrupted, please remove it and try again.'.format(DATABASE_FILE_PATH))
            cls.conn.close()
            exit(1)

    @classmethod
    def disconnect(cls):
        if not cls.conn: return

        cls.conn.close()
        cls.conn = None

    @classmethod
    def all(cls):
        if not cls.conn: return

        for record in cls.conn.execute('SELECT * FROM {TABLE_NAME};'.format(TABLE_NAME=TABLE_NAME)):
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

    def write(self):
        if not self.conn: return

        if self.exists():
            # record with same name exists
            print('Record with same name exists.')
            return

        cur = self.conn.cursor()
        cur.execute('''INSERT INTO {TABLE_NAME}
            (name, year, month, day)
            VALUES ("{name}", {year}, {month}, {day});'''.format(
            year=self.year,
            month=self.month,
            day=self.day,
            name=self.name,
            TABLE_NAME=TABLE_NAME)
        )
        self.conn.commit()
        print('Record [{new_record}] had been added into database.'.format(
            new_record=self,
            DATABASE_FILE=DATABASE_FILE_PATH,))

    def exists(self):
        if not self.conn: return

        cur = self.conn.cursor()
        cur.execute('''SELECT * FROM {TABLE_NAME} WHERE name='{name}'
            '''.format(name=self.name, TABLE_NAME=TABLE_NAME))

        return cur.fetchone() is not None
