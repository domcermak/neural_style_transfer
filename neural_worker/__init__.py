import json
from arbitrary_style_transfer import process
from common.utils import (
    rabbit_connect_and_make_channel,
    pg_connect_and_make_cursor,
    select_scheduled_image,
    insert_into_processed_images,
)
from PIL import Image

rabbitmq_connection, rabbitmq_channel = rabbit_connect_and_make_channel()
rabbitmq_channel.queue_declare(queue='nst_to_be_process')

pg_connection, pg_cursor = pg_connect_and_make_cursor()


def subscribe_callback(_ch, _method, _properties, body):
    print('subscribed')

    parsed_body = json.loads(body)
    scheduled_image_id = parsed_body['scheduled_image_id']
    content_image, style_image = select_scheduled_image(pg_cursor, scheduled_image_id)
    generated_image = process(content_image, style_image)
    insert_into_processed_images(pg_cursor, Image.fromarray(generated_image), scheduled_image_id)

    print("processed")


def main():
    rabbitmq_channel.basic_consume(queue='nst_to_be_process',
                                   on_message_callback=subscribe_callback,
                                   auto_ack=True)
    rabbitmq_channel.start_consuming()


if __name__ == '__main__':
    print('starting')
    main()
    print('quitting...')
