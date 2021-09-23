import tensorflow as tf
import numpy as np
from PIL import Image
from tensorflow.keras.applications import VGG19
from pathlib import Path
from common.utils import IMAGE_SHAPE

path_to_weigths = Path(__file__).parent.parent.joinpath(
    'data/weights/vgg19_weights_tf_dim_ordering_tf_kernels_notop.h5'
).absolute()
vgg = VGG19(include_top=False,
            input_shape=(IMAGE_SHAPE[0], IMAGE_SHAPE[1], 3),
            weights=path_to_weigths)
vgg.trainable = False
optimizer = tf.keras.optimizers.Adam(learning_rate=0.08)
STYLE_LAYERS = [
    ('block1_conv1', 0.2),
    ('block2_conv1', 0.2),
    ('block3_conv1', 0.2),
    ('block4_conv1', 0.2),
    ('block5_conv1', 0.2),
]


def compute_content_cost(content_output, generated_output):
    a_C = content_output[-1]
    a_G = generated_output[-1]

    m, n_H, n_W, n_C = a_G.get_shape().as_list()

    a_C_unrolled = tf.reshape(a_C, (m, n_H * n_W, n_C))
    a_G_unrolled = tf.reshape(a_G, (m, n_H * n_W, n_C))

    J_content = tf.reduce_sum(tf.square(a_C_unrolled - a_G_unrolled)) / (4 * n_H * n_W * n_C)

    return J_content


def gram_matrix(A):
    GA = tf.linalg.matmul(A, tf.transpose(A))

    return GA


def compute_layer_style_cost(a_S, a_G):
    m, n_H, n_W, n_C = a_G.get_shape().as_list()

    a_S = tf.transpose(tf.reshape(a_S, (n_H * n_W, n_C)))
    a_G = tf.transpose(tf.reshape(a_G, (n_H * n_W, n_C)))

    GS = gram_matrix(a_S)
    GG = gram_matrix(a_G)

    J_style_layer = tf.reduce_sum(tf.square(GS - GG)) / (4 * ((n_H * n_W) ** 2) * (n_C ** 2))

    return J_style_layer


def compute_style_cost(style_image_output, generated_image_output, STYLE_LAYERS=STYLE_LAYERS):
    J_style = 0

    a_S = style_image_output[:-1]
    a_G = generated_image_output[:-1]

    for i, weight in zip(range(len(a_S)), STYLE_LAYERS):
        J_style_layer = compute_layer_style_cost(a_S[i], a_G[i])
        J_style += weight[1] * J_style_layer

    return J_style


@tf.function()
def total_cost(J_content, J_style, alpha=10, beta=40):
    J = alpha * J_content + beta * J_style

    return J


def image_to_tensor(image):
    image = np.array(image)
    image = tf.constant(np.reshape(image, ((1,) + image.shape)))

    return image


def get_layer_outputs(vgg, layer_names):
    outputs = [vgg.get_layer(layer[0]).output for layer in layer_names]
    model = tf.keras.Model([vgg.input], outputs)

    return model


def clip_0_1(image):
    return tf.clip_by_value(image, clip_value_min=0.0, clip_value_max=1.0)


def tensor_to_image(tensor):
    tensor = tensor * 255
    tensor = np.array(tensor, dtype=np.uint8)
    if np.ndim(tensor) > 3:
        assert tensor.shape[0] == 1
        tensor = tensor[0]
    return Image.fromarray(tensor)


@tf.function()
def train_step(generated_image, a_S, a_C, vgg_model_outputs_func):
    with tf.GradientTape() as tape:
        tape.watch(generated_image)
        a_G = vgg_model_outputs_func(generated_image)

        J_style = compute_style_cost(a_S, a_G, STYLE_LAYERS=STYLE_LAYERS)
        J_content = compute_content_cost(a_C, a_G)
        J = total_cost(J_content, J_style, alpha=1, beta=2)

    grad = tape.gradient(J, generated_image)

    print(f"train c cost: {J_content}")
    print(f"train s cost: {J_style}")
    print(f"train cost: {J}")
    print(f"grad: {grad}")

    optimizer.apply_gradients([(grad, generated_image)])
    generated_image.assign(clip_0_1(generated_image))

    return J


def process(content_image, style_image):
    print(f"content_shape={np.array(content_image).shape} style_shape={np.array(style_image).shape}")

    content_image = image_to_tensor(content_image)
    style_image = image_to_tensor(style_image)
    generated_image = tf.Variable(tf.image.convert_image_dtype(content_image, tf.float32))

    content_layer = [('block5_conv4', 1)]
    vgg_model_outputs = get_layer_outputs(vgg, STYLE_LAYERS + content_layer)

    preprocessed_content = tf.Variable(tf.image.convert_image_dtype(content_image, tf.float32))
    a_C = vgg_model_outputs(preprocessed_content)

    preprocessed_style = tf.Variable(tf.image.convert_image_dtype(style_image, tf.float32))
    a_S = vgg_model_outputs(preprocessed_style)

    epochs = 100
    final_image = None
    for i in range(epochs):
        J = train_step(generated_image, a_S, a_C, vgg_model_outputs)
        print(f"Epoch {i}:")
        print(f"-> Cost: {J}")
        if i == epochs - 1:
            final_image = tensor_to_image(generated_image)

    return final_image
