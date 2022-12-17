import os
from datetime import datetime, timedelta

import dbConnector

UPLOAD_FOLDER = 'D:\\000FileBox'


def send_data_db(id_session, type, file_name_real, file_name_fs):
    db = dbConnector.create_connection()
    time_start = datetime.now()
    time_end = time_start + timedelta(minutes=30)
    query = 'insert into data (id_session, type, file_name_real, file_name_fs, time_birth, time_death, status) ' \
            'values (%s, %s, %s, %s, %s, %s, %s)'
    val = (id_session, type, file_name_real, file_name_fs, time_start, time_end, 'created')
    with db.cursor() as cursor:
        cursor.execute(query, val)
        db.commit()
    db.close()


def send_data_fs(file_name_fs, file):
    file.save(os.path.join(UPLOAD_FOLDER, file_name_fs))
