import io

import streamlit as st
from PIL import Image
from pathlib import Path
from os import listdir
from common.utils import IMAGE_SHAPE
from components.RadioButtonImages import choose_from_images


def __style_path():
    return Path(__file__).parent.parent.joinpath('assets').joinpath('style')


def __load_style_image_paths_and_labels():
    filenames = listdir(__style_path().absolute())
    labels = [filename.split('/')[-1].split('.')[0] for filename in filenames]
    image_paths = [__style_path().joinpath(filename).absolute() for filename in filenames]

    return image_paths, labels


def __select_filter():
    st.caption('Níže vyberte malbu jako vzor stylu:')
    image_paths, labels = __load_style_image_paths_and_labels()
    option = choose_from_images(image_paths, labels, size=150)

    _, center_col, _ = st.columns([.7, 1, .7])
    if center_col.button('Potvrdit výběr a odeslat ke zpracování'):
        print(f"selected {option}")
        return Image.open(image_paths[option]).resize(IMAGE_SHAPE)


def __resize_and_crop_image(image):
    # resize with aspect ratio
    image.thumbnail(IMAGE_SHAPE, Image.ANTIALIAS)

    width, height = image.size
    new_width, new_height = IMAGE_SHAPE

    left = round((width - new_width) / 2)
    top = round((height - new_height) / 2)
    x_right = round(width - new_width) - left
    x_bottom = round(height - new_height) - top
    right = width - x_right
    bottom = height - x_bottom

    return image.crop((left, top, right, bottom))


def display_upload_screen():
    uploaded_file = st.file_uploader("Vyberte obrázek k obarvení...", type=['jpg', 'jpeg', 'png'])
    if uploaded_file is not None:
        content_image = Image.open(uploaded_file)

        return __resize_and_crop_image(content_image), __select_filter()


def display_download_screen(images):
    cols = st.columns([1, 1, 1])
    for i, image in enumerate(images):
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG')

        cols[i % 3].image(image, use_column_width='always')
        cols[i % 3].download_button(
            label="Stáhnout obrázek",
            data=buffer,
            file_name="image.jpeg",
            mime="image/jpeg"
        )
