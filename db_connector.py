import mysql.connector
from configuration import config


def create_connection():
    connection = mysql.connector.connect(
        host=config.HOST,
        database=config.NAME,
        user=config.USER,
        password=config.PASSWORD
    )
    return connection
