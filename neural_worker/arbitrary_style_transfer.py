import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
from common.utils import IMAGE_SHAPE

print("TF Version: ", tf.__version__)
print("TF-Hub version: ", hub.__version__)
print("Eager mode enabled: ", tf.executing_eagerly())
print("GPU available: ", tf.config.list_physical_devices('GPU'))

print('loading hub')
hub_handle = 'https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2'
hub_module = hub.load(hub_handle)
print('hub loaded')


def convert_image_to_tf(image):
    image = np.array(image).astype(np.float32)[np.newaxis, ...] / 255.
    return tf.image.resize(image, IMAGE_SHAPE)


def process(content_image, style_image):
    c_img = convert_image_to_tf(content_image)
    s_img = convert_image_to_tf(style_image)

    outputs = hub_module(tf.constant(c_img), tf.constant(s_img))
    stylized_image = outputs[0]

    return np.array(stylized_image[0] * 256, dtype='uint8')
