import sqlite3
import os


HOME_DIR = os.path.expanduser("~")
DATABASE_FILE_NAME = '.birthday.sqlite'
DATABASE_FILE_PATH = os.path.join(HOME_DIR, DATABASE_FILE_NAME)
TABLE_NAME = 'Birthdays'


class Birthday:
    conn = None

    @classmethod
    def all(cls):
        if cls.conn == None:
            cls._check_db()
        for record in cls.conn.execute('SELECT * FROM {}'.format(TABLE_NAME)):
            yield Birthday(record)

    @classmethod
    def _check_db(cls):
        try:
            cls.conn = sqlite3.connect(DATABASE_FILE_PATH)
            cur = cls.conn.cursor()
            cur.execute('''SELECT name FROM sqlite_master
                    WHERE type="table" AND name="{table_name}";'''.format(table_name=TABLE_NAME))
            if cur.fetchone() is None:
                cur.execute('''CREATE TABLE "{table_name}" (
                        "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                        "year" INTEGER DEFAULT 0,
                        "month" INTEGER DEFAULT 0,
                        "day" INTEGER DEFAULT 0,
                        "name" TEXT DEFAULT "(empty)",
                        );'''.format(table_name=TABLE_NAME))
                cls.conn.commit()

        except sqlite3.DatabaseError as e:
            print('{} is corrupted, please remove it and try again.'.format(DATABASE_FILE_PATH))
            cls.conn.close()
            exit(1)

    def __init__(self, raw_record):
        self.year = raw_record[1]
        self.month = raw_record[2]
        self.day = raw_record[3]
        self.name = raw_record[4]

    def __str__(self):
        return '{:>04}/{:>02}/{:>02} {}'.format(
            self.year if self.year else '----',
            self.month if self.month else '--',
            self.day if self.day else '--',
            self.name
        )
