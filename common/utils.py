import os
import pika
import psycopg2 as pg


def rabbit_connect_and_make_channel():
    try:
        amqp_url = os.environ['AMQP_URL']
        parameters = pika.URLParameters(amqp_url)
    except KeyError:
        parameters = pika.ConnectionParameters('localhost')

    connection = pika.BlockingConnection(parameters=parameters)

    return connection, connection.channel()

def is_production():
    try:
        return os.environ['NST_ENV'] == 'production'
    except KeyError:
        False

def pg_connect_and_make_cursor():
    connection = pg.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="postgres")

    return connection, connection.cursor()
