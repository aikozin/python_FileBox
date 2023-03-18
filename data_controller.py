import os
import main
from datetime import datetime, timedelta
import db_connector


def send_data_db(id_session, type_file, file_name_real, file_name_fs):
    """
    Метод для обновления информации о данных в БД

    :param id_session: ID сессии
    :param type_file: тип данных
    :param file_name_real: настоящее имя файла
    :param file_name_fs: имя файла в файловой системе
    :return:
    """

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


def send_data_fs(file_name_fs, file):
    """
    Сохранение данных в виде файла в файловой системе

    :param file_name_fs: имя файла в файловой системе
    :param file: файл
    :return: -
    """

    file_path = os.path.join(main.UPLOAD_FOLDER, file_name_fs)
    file.save(file_path)


def get_user_files_info(id_session, status):
    """
    Получение списка файлов с заданным id_session и status

    :param id_session: ID сессии
    :param status: статус файла
    :return: массив файлов
    """

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
                "time_death": row[6]
            }
            json.append(file)
    db.close()
    return json


def get_file_info(id_file, id_session):
    """
    Получение информации о передаваемом файле с заданным id_file и id_session.

    :param id_file: ID файла (целое число)
    :param id_session: ID сессии
    :return: json файл с атрибутами передаваемого файла
    """

    db = db_connector.create_connection()
    query = 'SELECT * FROM data where id_file = %s and id_session = %s'
    val = (id_file, id_session)
    with db.cursor() as cursor:
        cursor.execute(query, val)
        result = cursor.fetchone()
        json = {
            "type": result[2],
            "file_name_real": result[3],
            "file_name_fs": result[4],
            "time_birth": result[5],
            "time_death": result[6],
            "status": result[7]
        }
    db.close()
    return json
