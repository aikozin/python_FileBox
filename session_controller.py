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
    time_end = time_start + timedelta(minutes=config.LIFE_TIME)
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

    query = 'UPDATE session SET mobile_ip=%s, mobile_agent=%s, WHERE id_session=%s'
    db = db_connector.create_connection()
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


def update_time_end(id_session, infinity=False):
    """
    Метод для обновления времени закрытия сессии

    :param id_session: ID сессии
    :param infinity: параметр для установки бесконечной времени жизни сессии, значение по умолчанию - False
    :return: -
    """
    current_time = datetime.now()
    time_end = current_time + timedelta(minutes=config.LIFE_TIME)
    if infinity:
        time_end = current_time + timedelta(days=config.INFINITY_LIFE_TIME)
    query = 'UPDATE session SET time_end = %s WHERE id_session = %s'
    db = db_connector.create_connection()
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


def session_close(id_session):
    """
    https://wiki.yandex.ru/homepage/moduli/rest-api/sessionclose---zakrytie-sessii-po-zhelaniju-klient/
    """
    query = 'UPDATE session SET time_end=%s, removal_flag=True WHERE id_session=%s'
    db = db_connector.create_connection()
    with db.cursor() as cursor:
        cursor.execute(query, id_session)
        db.commit()
    db.close()


def on_connect(id_session, device_sid, device_type):
    query = 'INSERT INTO client_sockets (id_session, sid_%s) VALUES (%s, %s) ' \
            'ON DUPLICATE KEY UPDATE sid_%s = %s'
    values = (device_type, id_session, device_sid, device_type, device_sid)
    db = db_connector.create_connection()
    with db.cursor() as cursor:
        cursor.execute(query, values)
        db.commit()
    db.close()
