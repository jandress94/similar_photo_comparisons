#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# img_downloader.py.py
# Author: Jim Andress
# Created: 2020-12-29


from io import BytesIO
import os
from PIL import Image
import requests
import time


URL_FILEPATH = 'data/natalie_img_urls.txt'

SAVE_LOC = 'data/datasets/wedding_photographers/images/natalie'


if __name__ == '__main__':
    with open(URL_FILEPATH, 'r') as fp:
        counter = 0
        for line in fp:
            response = requests.get(line.strip())
            img = Image.open(BytesIO(response.content))
            img.save(os.path.join(SAVE_LOC, f'img_{counter}.png'))

            time.sleep(2)
            counter += 1
