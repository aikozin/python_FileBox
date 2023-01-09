import os
import main
from datetime import datetime, timedelta

import db_connector


# -----------------------------------
# Метод для обновления информации о данных в БД
#
# param id_session: ID сессии
# param type_file: тип данных
# param file_name_real: настоящее имя файла
# param file_name_fs: имя файла в файловой системе
# return: -
# -----------------------------------
def send_data_db(id_session, type_file, file_name_real, file_name_fs):
    db = db_connector.create_connection()
    time_start = datetime.now()
    time_end = time_start + timedelta(minutes=30)
    query = 'insert into data (id_session, type, file_name_real, file_name_fs, time_birth, time_death, status) ' \
            'values (%s, %s, %s, %s, %s, %s, %s)'
    val = (id_session, type_file, file_name_real, file_name_fs, time_start, time_end, 'created')
    with db.cursor() as cursor:
        cursor.execute(query, val)
        db.commit()
    db.close()


# -----------------------------------
# Сохранение данных в виде файла в файловой системе
#
# param file_name_fs: имя файла в файловой системе
# param file: файл
# return: -
# -----------------------------------
def send_data_fs(file_name_fs, file):
    file_path = os.path.join(main.UPLOAD_FOLDER, file_name_fs)
    file.save(file_path)


# -----------------------------------
# Получение списка файлов с заданным id_session и status
#
# param id_session: ID сессии
# param status: статус файла
# return: массив файлов
# -----------------------------------
def get_files_info(id_session, status):
    json = list()
    db = db_connector.create_connection()
    query = 'select * from data where id_session=%s and status=%s'
    val = (id_session, status)
    with db.cursor() as cursor:
        cursor.execute(query, val)
        result = cursor.fetchall()
        for row in result:
            file = {
                "id": row[0],
                "type": row[2],
                "file_name_real": row[3],
                "file_name_fs": row[4],
                "time_birth": row[5],
                "time_death": row[6],
            }
            json.append(file)
    db.close()
    return json
