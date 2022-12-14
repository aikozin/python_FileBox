from datetime import datetime, timedelta

import dbConnector


# метод проверки использования id
def check_free_id(id):
    # думаем, что id не используется
    is_free_id = False
    # подключаемся к БД
    db = dbConnector.create_connection()
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
    db = dbConnector.create_connection()
    # получаем текущее время
    time_start = datetime.now().date()
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
