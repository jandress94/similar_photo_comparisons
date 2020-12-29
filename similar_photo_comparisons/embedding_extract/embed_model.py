#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# embed_model.py
# Author: Jim Andress
# Created: 2020-12-29

import tensorflow as tf


_model = None


def _create_model():
    resnet = tf.keras.applications.ResNet50V2(include_top=False, pooling='avg')
    resnet_out_pre_relu = resnet.get_layer('post_bn').output
    out = tf.keras.layers.GlobalAveragePooling2D()(resnet_out_pre_relu)
    resnet = tf.keras.Model(inputs=resnet.input, outputs=out)

    i = tf.keras.layers.Input([None, None, 3])
    x = tf.keras.applications.resnet_v2.preprocess_input(i)
    x = resnet(x)
    return tf.keras.Model(inputs=[i], outputs=[x])


def embed_img(image_filepath):
    global _model
    if _model is None:
        _model = _create_model()

    img = tf.image.decode_jpeg(tf.io.read_file(image_filepath))
    img = tf.expand_dims(img, axis=0)

    return _model(img)[0].numpy()
