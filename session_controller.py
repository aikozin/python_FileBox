from datetime import datetime, timedelta

import db_connector


def check_free_id(id_session):
    """
    Метод для проверки свободного ID сессии

    :param id_session: ID сессии
    :return: true, если ID свободен
    """

    # думаем, что id не используется
    is_free_id = False
    # подключаемся к БД
    db = db_connector.create_connection()
    # описываем запрос и значения для него
    query = 'select * from session where id_session=%s'
    val = (str(id_session),)
    # работа с БД
    with db.cursor() as cursor:
        # выполняем запрос
        cursor.execute(query, val)
        # результат запроса - в список
        result = cursor.fetchall()
        # если длина ответа (количество строк) = 0 - думаем, что такой id не использовался
        if len(result) == 0:
            is_free_id = True
    # закрываем коннект к БД
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

    # подключаемся к БД
    db = db_connector.create_connection()
    # получаем текущее время
    time_start = datetime.now()
    # к текущему времени прибавляем 5 минут
    time_end = time_start + timedelta(minutes=5)
    # описываем запрос и значения для него
    query = 'insert into session (id_session, time_start, time_end, web_ip, web_agent) values (%s, %s, %s, %s, %s)'
    val = (id_session, time_start, time_end, web_ip, web_agent)
    # работа с БД
    with db.cursor() as cursor:
        # выполняем запрос
        cursor.execute(query, val)
        # завершаем транзакцию
        db.commit()
    # закрываем коннект к БД
    db.close()


def session_mobile_connect(id_session, mobile_ip, mobile_agent):
    """
    Метод для подключения телефона к сессии после сканирования QR-кода

    :param id_session: ID сессии
    :param mobile_ip: IP адрес телефона
    :param mobile_agent: информация о системе телефона
    :return: -
    """

    # подключаемся к БД
    db = db_connector.create_connection()
    # описание запроса
    query = 'UPDATE session SET mobile_ip = %s, mobile_agent = %s WHERE id_session = %s'
    val = (mobile_ip, mobile_agent, id_session)
    # работа с БД
    with db.cursor() as cursor:
        # выполняем запрос
        cursor.execute(query, val)
        # завершаем транзакцию
        db.commit()
    # закрываем коннект к БД
    db.close()


def get_session_info(id_session):
    """
    Метод для получения всей информации о сессии

    :param id_session: ID сессии
    :return: список с информацией о сессии
    """

    # подключаемся к БД
    db = db_connector.create_connection()
    # описание запроса
    query = 'SELECT * FROM session WHERE id_session = %s'
    val = (id_session,)
    # работа с БД
    with db.cursor() as cursor:
        # выполняем запрос
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

    # получаем текущее время
    time_current = datetime.now()
    # к текущему времени прибавляем 5 минут
    time_end = time_current + timedelta(minutes=5)
    # подключаемся к БД
    db = db_connector.create_connection()
    # описание запроса
    query = 'UPDATE session SET time_end = %s WHERE id_session = %s'
    val = (time_end, id_session)
    # работа с БД
    with db.cursor() as cursor:
        # выполняем запрос
        cursor.execute(query, val)
        # завершаем транзакцию
        db.commit()
    # закрываем коннект к БД
    db.close()
