from datetime import datetime, timedelta
from configuration import config

import db_connector


def check_free_id(id_session):
    """
    Метод для проверки свободного ID сессии

    :param id_session: ID сессии
    :return: true, если ID свободен
    """

    is_free_id = False
    db = db_connector.create_connection()
    query = 'SELECT * FROM session WHERE id_session=%s'
    val = (str(id_session),)
    with db.cursor() as cursor:
        cursor.execute(query, val)
        result = cursor.fetchall()
        if len(result) == 0:
            is_free_id = True
    db.close()
    return is_free_id


def session_start(id_session, web_ip, web_agent):
    """
    Метод для старта сессии при подключении ПК к сайту

    :param id_session: ID сессии
    :param web_ip: IP адрес ПК
    :param web_agent: информация о браузере клиента
    :return: -
    """

    db = db_connector.create_connection()
    time_start = datetime.now()
    time_end = time_start + timedelta(minutes=5)
    query = 'insert into session (id_session, time_start, time_end, web_ip, web_agent) values (%s, %s, %s, %s, %s)'
    val = (id_session, time_start, time_end, web_ip, web_agent)
    with db.cursor() as cursor:
        cursor.execute(query, val)
        db.commit()
    db.close()


def session_mobile_connect(id_session, mobile_ip, mobile_agent):
    """
    Метод для подключения телефона к сессии после сканирования QR-кода

    :param id_session: ID сессии
    :param mobile_ip: IP адрес телефона
    :param mobile_agent: информация о системе телефона
    :return: -
    """

    db = db_connector.create_connection()
    query = 'UPDATE session SET mobile_ip = %s, mobile_agent = %s WHERE id_session = %s'
    val = (mobile_ip, mobile_agent, id_session)
    with db.cursor() as cursor:
        cursor.execute(query, val)
        db.commit()
    db.close()


def get_session_info(id_session):
    """
    Метод для получения всей информации о сессии

    :param id_session: ID сессии
    :return: список с информацией о сессии
    """

    db = db_connector.create_connection()
    query = 'SELECT * FROM session WHERE id_session = %s'
    val = (id_session,)
    with db.cursor() as cursor:
        cursor.execute(query, val)
        result = cursor.fetchone()
        row = {
            "id": result[0],
            "time_start": result[1],
            "time_end": result[2],
            "web_ip": result[3],
            "web_agent": result[4],
            "mobile_ip": result[5],
            "mobile_agent": result[6]
        }
    db.close()
    return row


def update_time_end(id_session):
    """
    Метод для обновления времени закрытия сессии

    :param id_session: ID сессии
    :return: -
    """

    time_current = datetime.now()
    time_end = time_current + timedelta(minutes=5)
    db = db_connector.create_connection()
    query = 'UPDATE session SET time_end = %s WHERE id_session = %s'
    val = (time_end, id_session)
    with db.cursor() as cursor:
        cursor.execute(query, val)
        db.commit()
    db.close()


def session_is_alive(id_session):
    """
    Метод проверяет актуальность сессии - наличие записи с полученным ID и ложность её флага на удаление

    :param id_session: ID сессии
    :return: bool (True при выполнении условия проверки)
    """
    db = db_connector.create_connection()
    query = 'SELECT id_session FROM session WHERE id_session=%s and removal_flag=False'
    val = (id_session,)
    with db.cursor() as cursor:
        cursor.execute(query, val)
        result = cursor.fetchall()
    db.close()
    return (False, True)[len(result)]


def keep_alive(id_session):
    """
    https://wiki.yandex.ru/homepage/moduli/rest-api/sessionkeep-alive/
    """
    time_end = datetime.now() + timedelta(minutes=config.LIFE_TIME)
    db = db_connector.create_connection()
    query_to_session = 'UPDATE session SET time_end = %s WHERE id_session = %s'
    query_to_data = 'UPDATE data SET time_death = %s WHERE id_session = %s'
    values = (time_end, id_session)
    with db.cursor() as cursor:
        cursor.execute(query_to_session, values)
        db.commit()
        cursor.execute(query_to_data, values)
        db.commit()
    db.close()
