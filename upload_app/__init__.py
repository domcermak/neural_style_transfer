import logging as log
import time

import streamlit as st
from screens import display_upload_screen, display_download_screen
import json
import numpy as np
from common.utils import (
    rabbit_connect_and_make_channel,
    is_production,
    pg_connect_and_make_cursor,
    insert_into_sessions,
    insert_into_scheduled_images,
    any_image_ready_to_download,
    select_images_to_download,
)
import uuid

if 'rabbitmq_channel' not in st.session_state:
    connection, channel = rabbit_connect_and_make_channel()
    channel.queue_declare(queue='nst_to_be_process')

    st.session_state['rabbitmq_channel'] = channel
else:
    channel = st.session_state['rabbitmq_channel']

if 'psql_connection' not in st.session_state:
    pg_connection, pg_cursor = pg_connect_and_make_cursor()

    st.session_state['psql_connection'] = {
        'cursor': pg_cursor,
        'conn': pg_connection,
    }

PG_CURSOR = st.session_state['psql_connection']['cursor']

if 'uuid' not in st.session_state:
    uuid = str(uuid.uuid4())
    st.session_state['uuid'] = uuid
    insert_into_sessions(PG_CURSOR, uuid, 'user')


def hideAdminHamburgerMenu():
    st.markdown(""" <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style> """, unsafe_allow_html=True)


def add_to_process_queue(content_image, style_image):
    scheduled_image_id = insert_into_scheduled_images(PG_CURSOR, content_image, style_image, st.session_state['uuid'])
    body = json.dumps({
        'scheduled_image_id': scheduled_image_id,
    })
    channel.basic_publish(exchange='',
                          routing_key='nst_to_be_process',
                          body=body)
    log.info('published')


def main():
    st.set_page_config(page_title='Umění pomocí umělé inteligence', page_icon=None)  # we could add one
    st.header('Umění pomocí umělé inteligence')

    if is_production():
        hideAdminHamburgerMenu()

    if 'state' not in st.session_state:
        st.session_state['state'] = 'upload'

    if st.session_state['state'] == 'wait':
        st.success('Vybrané obrázky byly přidány do zpracování. Nyní sledujte prezentaci.')

        if st.button("Nahrát další obrázek"):
            st.session_state['state'] = 'upload'
            st.experimental_rerun()

        while True:
            if any_image_ready_to_download(PG_CURSOR, st.session_state['uuid']):
                break
            time.sleep(1)

        st.success('Vámi zadané obrázky jsou připravené ke stažení')
        if st.button("Stáhnout vygenerovaný obrázek"):
            st.session_state['state'] = 'download'
            st.experimental_rerun()

    elif st.session_state['state'] == 'upload':
        images = display_upload_screen()
        if images is not None:
            log.info('images uploaded')
            content_image, style_image = images
            if content_image is not None and style_image is not None:
                add_to_process_queue(content_image, style_image)
                st.session_state['state'] = 'wait'
                st.experimental_rerun()

    elif st.session_state['state'] == 'download':
        images = select_images_to_download(PG_CURSOR, st.session_state['uuid'])
        display_download_screen(images)

        st.text("")
        if st.button("Nahrát další obrázek"):
            st.session_state['state'] = 'upload'
            st.experimental_rerun()


if __name__ == '__main__':
    log.info('starting')
    main()
    log.info('quitting...')
