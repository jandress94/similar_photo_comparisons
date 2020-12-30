#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# get_embeddings.py
# Author: Jim Andress
# Created: 2020-12-29

import argparse
import os
import pandas as pd
from tqdm import tqdm as tqdm

from similar_photo_comparisons.constants import IMAGE_DIRECTORY, EMBEDDING_DIRECTORY, EMBEDDINGS_FILENAME
from similar_photo_comparisons.utils import get_categories

from similar_photo_comparisons.embedding_extract.embed_model import embed_img


def get_image_paths(dataset_dir, category):
    category_image_dir = os.path.join(dataset_dir, IMAGE_DIRECTORY, category)
    image_filenames = [f for f in os.listdir(category_image_dir) if f != '.DS_Store']

    return [os.path.join(category_image_dir, im_fn) for im_fn in image_filenames]


def get_embeddings_for_category(category, dataset_dir):
    embeddings_dir = os.path.join(dataset_dir, EMBEDDING_DIRECTORY, category)
    os.makedirs(embeddings_dir, exist_ok=True)

    image_filepaths = get_image_paths(dataset_dir, category)

    print(f'Extracting {len(image_filepaths)} embeddings')

    embeddings = []
    for image_filepath in tqdm(image_filepaths):
        embedding = embed_img(image_filepath)
        embeddings.append(embedding)

    embeddings_df = pd.DataFrame(embeddings, columns=[f'embed_col_{i}' for i in range(embeddings[0].shape[0])], index=image_filepaths)
    return embeddings_df


def main():
    parser = argparse.ArgumentParser(description="Extracts the embeddings for the images",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("--dataset_directory", type=str, required=True,
                        help="Path to the directory where the dataset is saved")

    args = parser.parse_args()

    dataset_dir = args.dataset_directory

    categories = get_categories(dataset_dir)

    print(f'Found categories: {categories}')

    for category in categories:
        print(f'getting embeddings for category {category}')
        embeddings_df = get_embeddings_for_category(category, dataset_dir)
        embeddings_df.to_csv(os.path.join(dataset_dir, EMBEDDING_DIRECTORY, category, EMBEDDINGS_FILENAME))


if __name__ == '__main__':
    main()
