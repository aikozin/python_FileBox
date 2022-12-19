from datetime import datetime, timedelta

import db_connector


# -----------------------------------
# Метод для проверки свободного ID сессии
#
# param id_session: ID сессии
# return: true, если ID свободен
# -----------------------------------
def check_free_id(id_session):
    # думаем, что id не используется
    is_free_id = False
    # подключаемся к БД
    db = db_connector.create_connection()
    # описываем запрос и значения для него
    query = 'select * from session where id=%s'
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


# -----------------------------------
# Метод для старта сессии при подключении ПК к сайту
#
# param id: ID сессии
# param web_ip: IP адрес ПК
# param web_agent: информация о браузере клиента
# return: -
# -----------------------------------
def session_start(id_session, web_ip, web_agent):
    # подключаемся к БД
    db = db_connector.create_connection()
    # получаем текущее время
    time_start = datetime.now()
    # к текущему времени прибавляем 5 минут
    time_end = time_start + timedelta(minutes=5)
    # описываем запрос и значения для него
    query = 'insert into session (id, time_start, time_end, web_ip, web_agent) values (%s, %s, %s, %s, %s)'
    val = (id_session, time_start, time_end, web_ip, web_agent)
    # работа с БД
    with db.cursor() as cursor:
        # выполняем запрос
        cursor.execute(query, val)
        # завершаем транзакцию
        db.commit()
    # закрываем коннект к БД
    db.close()


# -----------------------------------
# Метод для подключения телефона к сессии после сканирования QR-кода
#
# param id: ID сессии
# param mobile_ip: IP адрес телефона
# param mobile_agent: информация о системе телефона
# return: -
# -----------------------------------
def session_mobile_connect(id_session, mobile_ip, mobile_agent):
    # подключаемся к БД
    db = db_connector.create_connection()
    # описание запроса
    query = 'UPDATE session SET mobile_ip = %s, mobile_agent = %s WHERE id = %s'
    val = (mobile_ip, mobile_agent, id_session)
    # работа с БД
    with db.cursor() as cursor:
        # выполняем запрос
        cursor.execute(query, val)
        # завершаем транзакцию
        db.commit()
    # закрываем коннект к БД
    db.close()


# -----------------------------------
# Метод для получения всей информации о сессии
#
# param id: ID сессии
# return: список с информацией о сессии
# -----------------------------------
def get_session_info(id_session):
    # подключаемся к БД
    db = db_connector.create_connection()
    # описание запроса
    query = 'SELECT * FROM session WHERE id = %s'
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


# -----------------------------------
# Метод для обновления времени закрытия сессии
#
# param id: ID сессии
# return: -
# -----------------------------------
def update_time_end(id_session):
    # получаем текущее время
    time_current = datetime.now()
    # к текущему времени прибавляем 5 минут
    time_end = time_current + timedelta(minutes=5)
    # подключаемся к БД
    db = db_connector.create_connection()
    # описание запроса
    query = 'UPDATE session SET time_end = %s WHERE id = %s'
    val = (time_end, id_session)
    # работа с БД
    with db.cursor() as cursor:
        # выполняем запрос
        cursor.execute(query, val)
        # завершаем транзакцию
        db.commit()
    # закрываем коннект к БД
    db.close()
