import os
from configuration import config
from datetime import datetime, timedelta
import db_connector


def send_data_db(id_session, type_file, file_name_real, file_name_fs, source):
    """
    Метод для обновления информации о данных в БД

    :param id_session: ID сессии
    :param type_file: тип данных
    :param file_name_real: настоящее имя файла
    :param file_name_fs: имя файла в файловой системе
    :param source: фиксированное значение источника файла WEB или MOBILE
    :return:
    """
    time_start = datetime.now()
    time_end = time_start + timedelta(minutes=config.LIFE_TIME)
    query = 'INSERT INTO data (id_session, type, file_name_real, file_name_fs, time_birth, time_death, status, ' \
            'source) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
    val = (id_session, type_file, file_name_real, file_name_fs, time_start, time_end, 'created', source)
    db = db_connector.create_connection()
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
    file_path = os.path.join(config.UPLOAD_FOLDER, file_name_fs)
    file.save(file_path)


def get_user_files_info(id_session):
    """
    Получение списка файлов с заданным id_session

    :param id_session: ID сессии
    :return: список словарей, хранящих пары "имя столбца - значение"
    """
    query = 'SELECT * FROM data WHERE id_session=%s'
    val = (id_session,)
    db = db_connector.create_connection()
    with db.cursor() as cursor:
        cursor.execute(query, val)
        response = [dict(zip(config.DATA_ROWS, value)) for value in cursor.fetchall()]
    db.close()
    return response


def get_file_info(id_file, id_session):
    """
    Получение информации о передаваемом файле с заданным id_file и id_session.

    :param id_file: ID файла (целое число)
    :param id_session: ID сессии
    :return: список словарей, хранящих пары "имя столбца - значение"
    """
    query = 'SELECT * FROM data where id = %s and id_session = %s'
    val = (id_file, id_session)
    db = db_connector.create_connection()
    with db.cursor() as cursor:
        cursor.execute(query, val)
        response = [dict(zip(config.DATA_ROWS, value)) for value in cursor.fetchone()]
    db.close()
    return response
