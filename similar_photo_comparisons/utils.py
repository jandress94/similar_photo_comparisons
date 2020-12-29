#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# utils.py
# Author: Jim Andress
# Created: 2020-12-29

import os

from similar_photo_comparisons.constants import IMAGE_DIRECTORY


def get_categories(dataset_dir, sub_dir=IMAGE_DIRECTORY):
    image_dir = os.path.join(dataset_dir, sub_dir)
    return [c for c in os.listdir(image_dir) if os.path.isdir(os.path.join(image_dir, c))]
