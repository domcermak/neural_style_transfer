import logging as log
import time
import streamlit as st
import json
from PIL import Image
import numpy as np
from common.utils import rabbit_connect_and_make_channel
import threading

if 'render_now' not in st.session_state:
    st.session_state['render_now'] = []


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

    log.debug('adding images')
    st.session_state['render_now'] = [content_image, style_image]
    log.debug('!!!! added !!!!')


def run_subscription():
    if 'rabbitmq_channel' not in st.session_state:
        connection, channel = rabbit_connect_and_make_channel()
        channel.queue_declare(queue='nst_to_be_process')
        channel.queue_declare(queue='nst_processed')

        st.session_state['rabbitmq_channel'] = channel
    else:
        channel = st.session_state['rabbitmq_channel']

    channel.basic_consume(queue='nst_processed',
                          on_message_callback=subscribe_callback,
                          auto_ack=True)
    channel.start_consuming()


def main():
    # Hides the top right hamburger menu
    # uncomment when the app is deployed
    #
    # hideAdminHamburgerMenu()

    st.set_page_config(page_title='Neural Style Transfer', page_icon=None)  # we could add one
    st.header('Zpracování Vámi nahraných fotek v reálném čase')

    th = threading.Thread(target=run_subscription)
    st.report_thread.add_report_ctx(th)
    th.start()
    th.join(0)

    while True:
        render_now = st.session_state['render_now']
        if len(render_now) > 0:
            log.debug('rendering')
            st.image(render_now)
            log.debug('rendered')
            st.session_state['render_now'] = []

        time.sleep(1)


if __name__ == '__main__':
    main()
    log.info('quitting...')
