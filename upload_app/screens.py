import streamlit as st
from PIL import Image
from pathlib import Path
from os import listdir


def __style_path():
    return Path(__file__).parent.parent.joinpath('data').joinpath('style')


def __load_style_images():
    filenames = listdir(__style_path().absolute())

    return [Image.open(__style_path().joinpath(filename).absolute()) for filename in filenames]


def __select_filter():
    images = [image.resize((250, 250)) for image in __load_style_images()]
    option_labels = [str(x) for x in range(1, len(images) + 1)]
    option = st.radio("Vyberte filter", options=option_labels)
    st.image(images, caption=option_labels, width=200)
    if st.button('Potvrdit výběr a odeslat ke zpracování'):
        print(f"selected {option}")
        return images[int(option) - 1]


def display_upload_screen():
    uploaded_file = st.file_uploader("Vyberte obrázek k obarvení...", type=['jpg', 'jpeg', 'png'])
    if uploaded_file is not None:
        content_image = Image.open(uploaded_file).resize((256, 256))

        return content_image, __select_filter()
