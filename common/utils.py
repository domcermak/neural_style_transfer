import os
import pika


def rabbit_connect_and_make_channel():
    try:
        amqp_url = os.environ['AMQP_URL']
        parameters = pika.URLParameters(amqp_url)
    except KeyError:
        parameters = pika.ConnectionParameters('localhost')

    connection = pika.BlockingConnection(parameters=parameters)

    return connection, connection.channel()
