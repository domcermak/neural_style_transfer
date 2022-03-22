import streamlit as st
from PIL import Image
from pathlib import Path
from os import listdir
from common.utils import IMAGE_SHAPE
from components.RadioButtonImages import choose_from_images


def __style_path():
    return Path(__file__).parent.parent.joinpath('data').joinpath('style')


def __load_style_image_paths_and_labels():
    filenames = listdir(__style_path().absolute())
    labels = [filename.split('/')[-1].split('.')[0] for filename in filenames]
    image_paths = [__style_path().joinpath(filename).absolute() for filename in filenames]

    return image_paths, labels


def __select_filter():
    st.caption('Níže vyberte malbu jako vzor stylu:')
    image_paths, labels = __load_style_image_paths_and_labels()
    option = choose_from_images(image_paths, labels, size=200)

    _, center_col, _ = st.columns([1, 1, 1])
    if center_col.button('Potvrdit výběr a odeslat ke zpracování'):
        print(f"selected {option}")
        return Image.open(image_paths[option])


def display_upload_screen():
    uploaded_file = st.file_uploader("Vyberte obrázek k obarvení...", type=['jpg', 'jpeg', 'png'])
    if uploaded_file is not None:
        content_image = Image.open(uploaded_file).resize(IMAGE_SHAPE)

        return content_image, __select_filter()
