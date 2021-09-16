import logging as log
import pathlib
import time
import streamlit as st
import json
from PIL import Image
import numpy as np
from common.utils import rabbit_connect_and_make_channel
import threading

if 'render_now' not in st.session_state:
    st.session_state['render_now'] = []

if 'qr_code' not in st.session_state:
    st.session_state['qr_code'] = None


def hideAdminHamburgerMenu():
    st.markdown(""" <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style> """, unsafe_allow_html=True)


def subscribe_callback(_ch, _method, _properties, body):
    log.debug('subscribed')

    parsed_body = json.loads(body)
    content_image = Image.fromarray(np.array(parsed_body['content_image'], dtype='uint8'))
    style_image = Image.fromarray(np.array(parsed_body['style_image'], dtype='uint8'))
    generated_image = Image.fromarray(np.array(parsed_body['generated_image'], dtype='uint8'))

    log.debug('adding images')
    st.session_state['render_now'].append({
        'content_image': content_image,
        'style_image': style_image,
        'generated_image': generated_image,
    })
    log.debug('!!!! added !!!!')


def run_subscription():
    if 'rabbitmq_channel' not in st.session_state:
        connection, channel = rabbit_connect_and_make_channel()
        channel.queue_declare(queue='nst_processed')

        st.session_state['rabbitmq_channel'] = channel
    else:
        channel = st.session_state['rabbitmq_channel']

    channel.basic_consume(queue='nst_processed',
                          on_message_callback=subscribe_callback,
                          auto_ack=True)
    channel.start_consuming()


def fetch_qr_code_image():
    try:
        path = pathlib.Path(__file__).parent.parent.joinpath('qr-code.png').absolute()
        return Image.open(path)
    except:
        return None


def main():
    # Hides the top right hamburger menu
    # uncomment when the app is deployed
    #
    # hideAdminHamburgerMenu()

    st.set_page_config(page_title='Neural Style Transfer', layout='wide', page_icon=None)  # we could add one
    st.title('Zpracování Vámi nahraných obrázků v reálném čase')

    col1, col2, col3 = st.columns([1, 2, 1])
    col1.header('Originální obrázek')
    col2.header('Vybraná malba')
    col3.header('Generovaný obrázek')

    col1_placeholder = col1.empty()
    col2_placeholder = col2.empty()
    col3_placeholder = col3.empty()

    th = threading.Thread(target=run_subscription)
    st.report_thread.add_report_ctx(th)
    th.start()
    th.join(0)

    while True:
        if st.session_state['qr_code'] is None:
            log.debug("fetching qr code")
            image = fetch_qr_code_image()
            if image is not None:
                log.info("qr code fetched")
                st.sidebar.header('Naskenujte pro zadání obrázku ke zpracování')
                st.sidebar.image(image=image)
                st.session_state['qr_code'] = image

        render_now = st.session_state['render_now']
        if len(render_now) > 0:
            st.session_state['render_now'] = []
            for images in render_now:
                col1_placeholder.empty()
                col2_placeholder.empty()
                col3_placeholder.empty()

                log.debug('rendering')
                col1_placeholder.image(images['content_image'], use_column_width=True)
                col2_placeholder.image(images['generated_image'], use_column_width=True)
                col3_placeholder.image(images['style_image'], use_column_width=True)
                log.debug('rendered')

                time.sleep(5)

        time.sleep(1)


if __name__ == '__main__':
    main()
    log.info('quitting...')
