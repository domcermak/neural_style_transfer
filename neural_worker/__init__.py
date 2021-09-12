import json
from PIL import Image
import numpy as np
from neural_style_transfer import process
from common.utils import rabbit_connect_and_make_channel, pg_connect_and_make_cursor
from datetime import datetime, timezone

rabbitmq_connection, rabbitmq_channel = rabbit_connect_and_make_channel()
rabbitmq_channel.queue_declare(queue='nst_to_be_process')
rabbitmq_channel.queue_declare(queue='nst_processed')

pg_connection, pg_cursor = pg_connect_and_make_cursor()


def create_init_image_batch(content_image, style_image):
    now = datetime.now(timezone.utc)
    pg_cursor.execute(
        """
        INSERT INTO public.image_batches (content_image, style_image, created_at, updated_at) 
        VALUES (?, ?, ?, ?)
        RETURNING id;
        """,
        (content_image, style_image, now, now),
    )
    image_batch_id = pg_cursor.fetchone()[0]

    return image_batch_id


def create_train_image_sample(image_batch_id, generated_image):
    now = datetime.now(timezone.utc)
    pg_cursor.execute(
        """
        BEGIN;
        UPDATE public.image_batches SET updated_at = ? WHERE id = ?;
        INSERT INTO public.image_batch_training_iteration_samples (image_batch_id, generated_image, created_at) 
        VALUES (?, ?, ?);
        COMMIT;
        """,
        (now, image_batch_id, image_batch_id, generated_image, now),
    )


def add_generated_image_to_image_batch(image_batch_id, generated_image):
    now = datetime.now(timezone.utc)
    pg_cursor.execute(
        """
        UPDATE public.image_batches SET generated_image = ?, processed_at = ?, updated_at = ? WHERE id = ?;
        """,
        (generated_image, now, now, image_batch_id),
    )


def add_to_processed_queue(content_image, style_image, generated_image):
    body = json.dumps({
        'content_image': np.array(content_image).tolist(),
        'style_image': np.array(style_image).tolist(),
        'generated_image': np.array(generated_image).tolist(),
    })
    rabbitmq_channel.basic_publish(exchange='',
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
    rabbitmq_channel.basic_consume(queue='nst_to_be_process',
                                   on_message_callback=subscribe_callback,
                                   auto_ack=True)
    rabbitmq_channel.start_consuming()


if __name__ == '__main__':
    print('starting')
    main()
    # connection.close()
    print('quitting...')
