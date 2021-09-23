import streamlit as st
from PIL import Image
from pathlib import Path
from os import listdir
from common.utils import IMAGE_SHAPE


def __style_path():
    return Path(__file__).parent.parent.joinpath('data').joinpath('style')


def __load_style_images():
    filenames = listdir(__style_path().absolute())
    labels = [filename.split('/')[-1].split('.')[0] for filename in filenames]

    return [Image.open(__style_path().joinpath(filename).absolute()) for filename in filenames], labels


def __select_filter():
    images, labels = __load_style_images()
    images = [image.resize(IMAGE_SHAPE) for image in images]
    option_labels = [f"{x} - {labels[x - 1]}" for x in range(1, len(images) + 1)]

    st.caption('Níže vyberte malbu jako vzor stylu:')
    col1, col2 = st.columns(2)
    col1.image(images, caption=option_labels, width=100)

    option = col2.radio("Vyberte malbu:", options=option_labels)
    if col2.button('Potvrdit výběr a odeslat ke zpracování'):
        print(f"selected {option}")
        return images[int(option.split(' ')[0]) - 1]


def display_upload_screen():
    uploaded_file = st.file_uploader("Vyberte obrázek k obarvení...", type=['jpg', 'jpeg', 'png'])
    if uploaded_file is not None:
        content_image = Image.open(uploaded_file).resize(IMAGE_SHAPE)

        return content_image, __select_filter()
