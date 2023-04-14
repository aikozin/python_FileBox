from datetime import datetime, timedelta
from configuration import config
import db_connector


def check_free_id(id_session):
    """
    Метод для проверки свободного ID сессии

    :param id_session: ID сессии
    :return: true, если ID свободен
    """
    query = 'SELECT * FROM session WHERE id_session=%s'
    val = (str(id_session),)
    db = db_connector.create_connection()
    with db.cursor() as cursor:
        cursor.execute(query, val)
        result = cursor.fetchall()
    db.close()
    return (True, False)[len(result)]


def session_start(id_session, web_ip, web_agent):
    """
    Метод для старта сессии при подключении ПК к сайту

    :param id_session: ID сессии
    :param web_ip: IP адрес ПК
    :param web_agent: информация о браузере клиента
    :return: -
    """
    time_start = datetime.now()
    time_end = time_start + timedelta(minutes=config.LIFE_TIME)
    query = 'INSERT INTO session (id_session, time_start, time_end, web_ip, web_agent) VALUES (%s, %s, %s, %s, %s)'
    val = (id_session, time_start, time_end, web_ip, web_agent)
    db = db_connector.create_connection()
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
    query = 'UPDATE session SET mobile_ip=%s, mobile_agent=%s WHERE id_session=%s'
    val = (mobile_ip, mobile_agent, id_session)
    db = db_connector.create_connection()
    with db.cursor() as cursor:
        cursor.execute(query, val)
        db.commit()
    db.close()


def get_session_info(id_session):
    """
    Метод для получения всей информации о сессии

    :param id_session: ID сессии
    :return: словарь с информацией о сессии в виде пар "имя столбца - значение"
    """
    query = 'SELECT * FROM session WHERE id_session = %s'
    val = (id_session,)
    db = db_connector.create_connection()
    with db.cursor() as cursor:
        cursor.execute(query, val)
        response = {row_name: value for row_name, value in zip(config.SESSION_ROWS, cursor.fetchone())}
    db.close()
    return response


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
    val = (time_end, id_session)
    db = db_connector.create_connection()
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
    query = 'SELECT * FROM session WHERE id_session=%s AND removal_flag=False'
    val = (id_session,)
    db = db_connector.create_connection()
    with db.cursor() as cursor:
        cursor.execute(query, val)
        result = cursor.fetchall()
    db.close()
    return bool(result)


def keep_alive(id_session):
    """
    https://wiki.yandex.ru/homepage/moduli/rest-api/sessionkeep-alive/
    """
    time_end = datetime.now() + timedelta(minutes=config.LIFE_TIME)
    query_to_session = 'UPDATE session SET time_end = %s WHERE id_session = %s'
    query_to_data = 'UPDATE data SET time_death = %s WHERE id_session = %s'
    values = (time_end, id_session)
    db = db_connector.create_connection()
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
    """
    При подключении нового пользователя к сокету создаёт в БД новую запись или обновляет уже существующую
    https://wiki.yandex.ru/homepage/moduli/rest-api/notifikator-changes/
    """
    query = "INSERT INTO client_sockets (id_session, sid_{type}) VALUES ('{id}', '{sid}') " \
            "ON DUPLICATE KEY UPDATE sid_{type} = '{sid}'".format(type=device_type, id=id_session, sid=device_sid)
    db = db_connector.create_connection()
    with db.cursor() as cursor:
        cursor.execute(query)
        db.commit()
    db.close()


def get_sid(id_session):
    """
    Получает socket ID по ID сессии.
    """
    query = "SELECT sid_mobile, sid_web FROM client_sockets WHERE id_session='{id}'".format(id=id_session)
    db = db_connector.create_connection()
    with db.cursor() as cursor:
        cursor.execute(query)
        result = tuple(*cursor.fetchall())
    db.close()
    return result
