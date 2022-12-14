import mysql.connector


def create_connection():
    connection = mysql.connector.connect(
        host='veshpedcoll.ml',
        database='filebox',
        user='user',
        password='database1604'
    )
    return connection
