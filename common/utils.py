import os
import pika
import psycopg2 as pg

IMAGE_SHAPE = (256, 256)


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
        host=pg_host(),
        database='postgres',
        user='postgres',
        password='postgres')

    return connection, connection.cursor()


def pg_host():
    host = os.environ['PG_HOST']

    return 'localhost' if host == '' else host
