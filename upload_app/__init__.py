import logging as log
import streamlit as st
from screens import display_upload_screen
import json
import numpy as np
from common.utils import rabbit_connect_and_make_channel, is_production

if 'rabbitmq_channel' not in st.session_state:
    connection, channel = rabbit_connect_and_make_channel()
    channel.queue_declare(queue='nst_to_be_process')

    st.session_state['rabbitmq_channel'] = channel
else:
    channel = st.session_state['rabbitmq_channel']


def hideAdminHamburgerMenu():
    st.markdown(""" <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style> """, unsafe_allow_html=True)


def add_to_process_queue(content_image, style_image):
    body = json.dumps({
        'content_image': np.array(content_image).tolist(),
        'style_image': np.array(style_image).tolist()
    })
    channel.basic_publish(exchange='',
                          routing_key='nst_to_be_process',
                          body=body)
    log.debug('published')


def main():
    if is_production():
        hideAdminHamburgerMenu()

    st.set_page_config(page_title='Umění pomocí umělé inteligence', page_icon=None)  # we could add one
    st.header('Umění pomocí umělé inteligence')
    if 'state' not in st.session_state:
        st.session_state['state'] = 'upload'

    if st.session_state['state'] == 'wait':
        st.success('Vybrané obrázky byly přidány do zpracování. Nyní sledujte prezentaci.')

        if st.button("Nahrát další obrázek"):
            st.session_state['state'] = 'upload'
            st.experimental_rerun()

    else:
        images = display_upload_screen()
        if images is not None:
            log.info('images uploaded')
            content_image, style_image = images
            if content_image is not None and style_image is not None:
                add_to_process_queue(content_image, style_image)
                st.session_state['state'] = 'wait'
                st.experimental_rerun()


if __name__ == '__main__':
    log.info('starting')
    main()
    # connection.close()
    log.info('quitting...')
