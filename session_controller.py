from datetime import datetime, timedelta

import db_connector


# метод проверки использования id
def check_free_id(id):
    # думаем, что id не используется
    is_free_id = False
    # подключаемся к БД
    db = db_connector.create_connection()
    # описываем запрос и значения для него
    query = 'select * from session where id=%s'
    val = (str(id),)
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


# метод для старта сессии
def session_start(id, web_ip, web_agent):
    # подключаемся к БД
    db = db_connector.create_connection()
    # получаем текущее время
    time_start = datetime.now()
    # к текущему времени прибавляем 5 минут
    time_end = time_start + timedelta(minutes=5)
    # описываем запрос и значения для него
    query = 'insert into session (id, time_start, time_end, web_ip, web_agent) values (%s, %s, %s, %s, %s)'
    val = (id, time_start, time_end, web_ip, web_agent)
    # работа с БД
    with db.cursor() as cursor:
        # выполняем запрос
        cursor.execute(query, val)
        # завершаем транзакцию
        db.commit()
    # закрываем коннект к БД
    db.close()


# метод коннекта телефона к сессии
def session_mobile_connect(id, mobile_ip, mobile_agent):
    # подключаемся к БД
    db = db_connector.create_connection()
    # описание запроса
    query = 'UPDATE session SET mobile_ip = %s, mobile_agent = %s WHERE id = %s'
    val = (mobile_ip, mobile_agent, id)
    # работа с БД
    with db.cursor() as cursor:
        # выполняем запрос
        cursor.execute(query, val)
        # завершаем транзакцию
        db.commit()
    # закрываем коннект к БД
    db.close()


def get_session_info(id):
    # подключаемся к БД
    db = db_connector.create_connection()
    # описание запроса
    query = 'SELECT * FROM session WHERE id = %s'
    val = (id,)
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


def update_time_end(id):
    # получаем текущее время
    time_current = datetime.now()
    # к текущему времени прибавляем 5 минут
    time_end = time_current + timedelta(minutes=5)
    # подключаемся к БД
    db = db_connector.create_connection()
    # описание запроса
    query = 'UPDATE session SET time_end = %s WHERE id = %s'
    val = (time_end, id)
    # работа с БД
    with db.cursor() as cursor:
        # выполняем запрос
        cursor.execute(query, val)
        # завершаем транзакцию
        db.commit()
    # закрываем коннект к БД
    db.close()
