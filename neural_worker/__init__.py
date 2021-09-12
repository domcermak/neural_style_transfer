import json
from PIL import Image
import numpy as np
from neural_style_transfer import process
from common.utils import rabbit_connect_and_make_channel

connection, channel = rabbit_connect_and_make_channel()
channel.queue_declare(queue='nst_to_be_process')
channel.queue_declare(queue='nst_processed')


def add_to_processed_queue(content_image, style_image, generated_image):
    body = json.dumps({
        'content_image': np.array(content_image).tolist(),
        'style_image': np.array(style_image).tolist(),
        'generated_image': np.array(generated_image).tolist(),
    })
    channel.basic_publish(exchange='',
                          routing_key='nst_processed',
                          body=body)

    print('published')


def subscribe_callback(_ch, _method, _properties, body):
    print('subscribed')

    parsed_body = json.loads(body)
    content_image = Image.fromarray(np.array(parsed_body['content_image'], dtype='uint8'))
    style_image = Image.fromarray(np.array(parsed_body['style_image'], dtype='uint8'))
    generated_image = process(content_image, style_image)

    add_to_processed_queue(content_image, style_image, generated_image)


def main():
    print('starting')
    channel.basic_consume(queue='nst_to_be_process',
                              on_message_callback=subscribe_callback,
                              auto_ack=True)
    channel.start_consuming()


if __name__ == '__main__':
    print('starting')
    main()
    #connection.close()
    print('quitting...')
