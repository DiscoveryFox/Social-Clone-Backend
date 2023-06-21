import sqlite3
import os
from . import config


class Database:
    def __init__(self, database_path: str = config.DATABASE_PATH) -> None:
        self.database_path: str = database_path
        self.connection = sqlite3.connect(config.DATABASE_PATH, timeout=config.DATABASE_TIMEOUT)

    def init_database(self) -> None:
        """
        Initializes the database.
        :return: None
        """
        cursor = self.connection.cursor()
        cursor.execute('''
CREATE TABLE IF NOT EXISTS files (
    hash TEXT PRIMARY KEY,
    file_path TEXT UNIQUE 
);''')
        self.connection.commit()
        cursor.close()

    def upload_post(self, post: bytes, hash_val: str):
        if self.check_for_existence(hash_val):
            return hash_val
        else:

            with open(os.path.join(config.STORAGE_PATH, hash_val), 'wb') as file_to_store:
                file_to_store.write(post)

            cursor = self.connection.cursor()
            cursor.execute('INSERT INTO files (hash, file_path) VALUES (?, ?);',
                           (hash_val, f'{config.STORAGE_PATH}/{hash_val}'))

            self.connection.commit()
            cursor.close()

            return hash_val

    def check_for_existence(self, hash_val: str):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM files WHERE hash = ?', (hash_val,))
        result = cursor.fetchone()
        print(result)
        cursor.close()
        return False if not result else True

    def delete_post(self, hash_val: str):
        cursor = self.connection.cursor()
        if self.check_for_existence(hash_val):
            cursor.execute('SELECT file_path FROM files WHERE hash = ?', (hash_val, ))
            file_path: str = cursor.fetchone()[0]
            try:
                os.remove(file_path)
            except FileNotFoundError:
                pass
            except OSError:
                return False
            cursor.execute('DELETE FROM files WHERE hash = ?', (hash_val,))
            self.connection.commit()
            cursor.close()
            return True
        else:
            return True

