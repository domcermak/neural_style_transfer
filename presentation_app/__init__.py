import logging as log
import pathlib
import time
import streamlit as st
from PIL import Image
from common.utils import (
    is_production,
    pg_connect_and_make_cursor,
    insert_into_sessions,
    select_unpresented_images,
)
import uuid

if 'qr_code' not in st.session_state:
    st.session_state['qr_code'] = None

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
    insert_into_sessions(PG_CURSOR, uuid, 'presentation')


def hideAdminHamburgerMenu():
    st.markdown(""" <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style> """, unsafe_allow_html=True)


def fetch_qr_code_image():
    try:
        path = pathlib.Path(__file__).parent.parent.joinpath('qr-code.png').absolute()
        return Image.open(path)
    except:
        return None


def main():
    st.set_page_config(page_title='Neural Style Transfer', layout='wide', page_icon=None)  # we could add one
    st.title('Malba z fotky pomocí umělé inteligence')

    if is_production():
        hideAdminHamburgerMenu()

    col1, _, col2 = st.columns([1, .2, 2])

    col1.header('Vybrané obrázky')
    col2.header('Výsledná malba')
    col1_placeholder1 = col1.empty()
    col1_placeholder2 = col1.empty()
    col1_placeholder3 = col1.empty()
    col2_placeholder = col2.empty()

    while True:
        if st.session_state['qr_code'] is None:
            log.info("fetching qr code")
            image = fetch_qr_code_image()
            if image is not None:
                st.sidebar.markdown('<div style="display: block; margin-top: 10rem"></div>', unsafe_allow_html=True)
                log.info("qr code fetched")
                st.sidebar.title('1. Naskenujte QR kód')
                st.sidebar.title('2. Vyberte nebo vyfoťte obrázek, ze kterého chcete vytvořil malbu')
                st.sidebar.title('3. Vyberte obrázek ze kterého má být použitý styl výsledné malby')
                st.sidebar.title('4. Sledujte prezentaci')
                st.sidebar.image(image=image)
                st.session_state['qr_code'] = image

        session_uuid = st.session_state['uuid']
        rows = select_unpresented_images(PG_CURSOR, session_uuid)
        if len(rows) > 0:
            for images in rows:
                col1_placeholder1.empty()
                col1_placeholder2.empty()
                col1_placeholder3.empty()
                col2_placeholder.empty()

                log.debug('rendering')
                col1_placeholder1.image(images['content_image'], use_column_width=True)
                col1_placeholder2.markdown("<h1 style='text-align: center; color: white;'>+</h1>",
                                           unsafe_allow_html=True)
                col1_placeholder3.image(images['style_image'], use_column_width=True)
                col2_placeholder.image(images['generated_image'], use_column_width=True)
                log.debug('rendered')

                time.sleep(5)

        time.sleep(1)


if __name__ == '__main__':
    main()
    log.info('quitting...')
