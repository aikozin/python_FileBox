import mysql.connector
from configuration import config


def create_connection():
    connection = mysql.connector.connect(
        host=config.HOST,
        database=config.NAME,
        user=config.USER,
        password=config.PASSWORD
    )

    # connection = mysql.connector.connect(
    #     host='veshpedcoll.ml',
    #     # host='localhost',
    #     database='filebox',
    #     user='user',
    #     password='database1604'
    # )
    return connection
