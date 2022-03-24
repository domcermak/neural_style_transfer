import io
import os
import pika
import psycopg2 as pg
from datetime import datetime, timezone
from PIL import Image

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
        return False


def insert_into_sessions(cursor, uuid, session_type):
    cursor.execute(
        """
        INSERT INTO public.sessions (uuid, type) VALUES (%s, %s);
        """,
        (uuid, session_type),
    )


def insert_into_scheduled_images(cursor, content_image, style_image, user_uuid):
    cursor.execute(
        """
        SELECT id FROM public.sessions WHERE "type" = 'user' AND "uuid" = %s LIMIT 1;
        """,
        (user_uuid,),
    )
    session_id = cursor.fetchone()[0]

    cursor.execute(
        """
        INSERT INTO public.scheduled_images (user_session_id, content_image, style_image) 
        VALUES (%s, %s, %s)
        RETURNING id;
        """,
        (session_id, __encode_img(content_image), __encode_img(style_image)),
    )

    scheduled_image_id = cursor.fetchone()[0]

    return scheduled_image_id


def select_scheduled_image(cursor, scheduled_image_id):
    cursor.execute(
        """
        SELECT content_image, style_image FROM public.scheduled_images WHERE id = %s LIMIT 1;
        """,
        (scheduled_image_id,),
    )
    row = cursor.fetchone()
    content, style = __decode_img(row[0]), __decode_img(row[1])

    return content, style


def insert_into_processed_images(cursor, generated_image, scheduled_image_id):
    cursor.execute(
        """
        SELECT id FROM public.sessions WHERE "type" = 'presentation';
        """,
    )
    rows = cursor.fetchall()

    if len(rows) == 0:
        print('no presentations are running')

    cursor.execute(
        """
        INSERT INTO public.generated_images (generated_image)
        VALUES (%s)
        RETURNING id
        """,
        (__encode_img(generated_image),),
    )
    generated_image_id = cursor.fetchone()[0]

    for row in rows:
        presentation_session_id = row[0]

        cursor.execute(
            """
            INSERT INTO public.processed_images (presentation_session_id, scheduled_image_id, generated_image_id, created_at)
            VALUES (%s, %s, %s, %s);
            """,
            (presentation_session_id, scheduled_image_id, generated_image_id, datetime.now(timezone.utc)),
        )


def select_unpresented_images(cursor, presentation_session_uuid):
    cursor.execute(
        """
        SELECT 
            pi.id,
            si.content_image,
            si.style_image,
            gi.generated_image 
        FROM 
            public.scheduled_images AS si INNER JOIN public.processed_images AS pi ON si.id = pi.scheduled_image_id
            INNER JOIN public.sessions AS ss ON ss.id = pi.presentation_session_id
            inner join public.generated_images as gi on gi.id = pi.generated_image_id
        WHERE
            ss.type = 'presentation' AND 
            ss.uuid = %s AND 
            pi.presented = false
        GROUP BY
            pi.id,
            si.content_image,
            si.style_image,
            gi.generated_image;
        """,
        (presentation_session_uuid,),
    )
    rows = cursor.fetchall()
    ids = []
    images = []
    for row in rows:
        processed_image_id = row[0]
        content = row[1]
        style = row[2]
        generated = row[3]

        ids.append(processed_image_id)
        images.append({
            'content_image': __decode_img(content),
            'style_image': __decode_img(style),
            'generated_image': __decode_img(generated),
        })

    if len(ids) > 0:
        cursor.execute(
            """
            UPDATE public.processed_images SET presented = true WHERE id IN (%s);
            """,
            tuple(ids),
        )

    return images


def any_image_ready_to_download(cursor, user_uuid):
    cursor.execute(
        """
        select count(gi.id) 
        from 
            public.sessions as ss join public.scheduled_images si on ss.id = si.user_session_id
            join public.processed_images pi on si.id = pi.scheduled_image_id
            join public.generated_images gi on gi.id = pi.generated_image_id
        where ss.uuid = %s and ss.type = 'user'
        group by gi.id;
        """,
        (user_uuid,)
    )
    try:
        count = cursor.fetchone()[0]
    except TypeError:
        count = 0

    return count > 0


def select_images_to_download(cursor, user_uuid):
    cursor.execute(
        """
        select gi.id, gi.generated_image
        from 
            public.sessions as ss join public.scheduled_images si on ss.id = si.user_session_id
            join public.processed_images pi on si.id = pi.scheduled_image_id
            join public.generated_images gi on gi.id = pi.generated_image_id
        where ss.uuid = %s and ss.type = 'user'
        group by gi.id, gi.generated_image;
        """,
        (user_uuid,)
    )
    rows = cursor.fetchall()
    images = []
    for row in rows:
        image = __decode_img(row[1])
        images.append(image)

    return images

def pg_connect_and_make_cursor():
    connection = pg.connect(
        host=__pg_host(),
        database='postgres',
        user='postgres',
        password='postgres')
    connection.autocommit = True

    return connection, connection.cursor()


def __encode_img(img):
    output = io.BytesIO()
    img.save(output, format='JPEG')

    return pg.Binary(output.getvalue())


def __decode_img(binary):
    return Image.open(io.BytesIO(binary))


def __pg_host():
    try:
        host = os.environ['PG_HOST']
    except KeyError:
        host = 'localhost'

    return 'localhost' if host == '' else host
