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
        while not self.stop.wait(15):
            trash_proc()


def trash_proc():
    # print(f'\ntrash_collector is in progress...{datetime.now()}')  # {datetime.now():%y-%m-%d %H:%M:%S}
    db = db_connector.create_connection()
    with db.cursor() as cursor:
        cursor.execute('UPDATE session SET removal_flag = True WHERE now() > time_end')
        db.commit()
        cursor.execute('SELECT id_session FROM session WHERE removal_flag = True')
        sessions_to_delete = tuple(*[cursor.fetchall()])
    if sessions_to_delete:
        files_to_delete = set()  # контейнер для хранения имён файлов вида {'file_name_fs.txt', ...}
        data_query = 'SELECT file_name_fs FROM data WHERE id_session = %s'
        for value in sessions_to_delete:
            with db.cursor() as cursor:
                cursor.execute(data_query, value)
                # ответ от БД имеет вид {('file_name_fs.txt',)}
                # распаковываем до вида {'file_name_fs.txt',}
                [files_to_delete.add(*file_name_fs) for file_name_fs in cursor.fetchall()]
        session_query = 'DELETE FROM session WHERE id_session = %s'
        for value in sessions_to_delete:
            with db.cursor() as cursor:
                cursor.execute(session_query, value)
                db.commit()
        db.close()
        if files_to_delete:
            [os.remove(os.path.join(config.UPLOAD_FOLDER, file_name_fs)) for file_name_fs in files_to_delete
             if os.path.exists(os.path.join(config.UPLOAD_FOLDER, file_name_fs))]
            # print(f'Files deleted: {files_to_delete}')
    # return print(f'\nSessions deleted: {sessions_to_delete}{datetime.now()}' if sessions_to_delete
    #              else f'\nNothing was deleted...{datetime.now()}')


trash_collector = TrashCollector()
