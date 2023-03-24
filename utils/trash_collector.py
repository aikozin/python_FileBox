import os
import db_connector
import threading
from datetime import datetime
from configuration import config


class TrashCollector(threading.Thread):
    def __init__(self):
        super().__init__()
        self.stop = threading.Event()

    def run(self):
        while not self.stop.wait(10):
            trash_proc()


def trash_proc():
    # print(f'\ntrash_collector in progress...{datetime.now()}')  # {datetime.now():%y-%m-%d %H:%M:%S}
    deletes_data = set()  # контейнер для хранения имён файлов вида {'file_name_fs.txt', ...}
    db = db_connector.create_connection()
    query = 'SELECT id_session FROM session WHERE now() > time_end'
    with db.cursor() as cursor:
        cursor.execute(query)
        deletes_sessions = tuple((id_session for id_session in cursor.fetchall()))

    data_query = 'SELECT file_name_fs FROM data WHERE now() > time_death'
    with db.cursor() as cursor:
        cursor.execute(data_query)
        [deletes_data.add(*file_name_fs) for file_name_fs in cursor.fetchall()]

    if deletes_sessions:
        data_query = 'SELECT file_name_fs FROM data WHERE id_session = %s'
        for value in deletes_sessions:
            with db.cursor() as cursor:
                cursor.execute(data_query, value)
                # ответ от БД имеет вид {('file_name_fs.txt',)}
                # распаковываем до вида {'file_name_fs.txt',}
                [deletes_data.add(*file_name_fs) for file_name_fs in cursor.fetchall()]

        session_query = 'DELETE FROM session WHERE id_session = %s'
        for value in deletes_sessions:
            with db.cursor() as cursor:
                cursor.execute(session_query, value)
                db.commit()
        db.close()

    if deletes_data:
        [os.remove(os.path.join(config.UPLOAD_FOLDER, file_name_fs)) for file_name_fs in deletes_data
         if os.path.exists(os.path.join(config.UPLOAD_FOLDER, file_name_fs))]
    #     print(f'Files deleted: {deletes_data}')
    # return print(f'\nSessions deleted: {deletes_sessions}{datetime.now()}' if deletes_sessions
    #              else f'\nNothing was deleted...{datetime.now()}')


trash_collector = TrashCollector()
