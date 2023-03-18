import os
import db_connector
import threading


class TrashCollector(threading.Thread):
    def __init__(self):
        super().__init__()
        self.stop = threading.Event()

    def run(self):
        while not self.stop.wait(10):
            proc_to_call()


def proc_to_call():
    db = db_connector.create_connection()
    query = 'SELECT id_session FROM session WHERE now() > time_end'
    with db.cursor() as cursor:
        cursor.execute(query)
        deletes_sessions = tuple((id_session for id_session in cursor.fetchall()))

    data_query = 'SELECT file_name_fs FROM data WHERE id_session = %s'
    deletes_data = set()
    for value in deletes_sessions:
        with db.cursor() as cursor:
            cursor.execute(data_query, value)
            # deletes_data.add(*cursor.fetchall())
            [deletes_data.add(name) for name in cursor.fetchall()]
    data_query = 'SELECT file_name_fs FROM data WHERE now() > time_death'
    with db.cursor() as cursor:
        cursor.execute(data_query)
        [deletes_data.add(name) for name in cursor.fetchall()]

    session_query = 'DELETE FROM session WHERE id_session = %s'
    for value in deletes_sessions:
        with db.cursor() as cursor:
            cursor.execute(session_query, value)
            db.commit()
    db.close()
    [os.remove(*file_path) for file_path in deletes_data if os.path.exists(*file_path)]


def start():
    trash_collector = TrashCollector()
    trash_collector.start()
