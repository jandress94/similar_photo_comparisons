#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# detect_similar_images.py
# Author: Jim Andress
# Created: 2020-12-29


import argparse
import os
import pandas as pd
from scipy.spatial.distance import cdist

from similar_photo_comparisons.constants import EMBEDDING_DIRECTORY, EMBEDDINGS_FILENAME, SIMILAR_IMAGES_DIRECTORY, SIMILAR_IMAGES_FILENAME
from similar_photo_comparisons.utils import get_categories


def get_similar_images(dataset_dir, cat1, cat2, metric, cutoff):
    cat1_embeds_df = pd.read_csv(os.path.join(dataset_dir, EMBEDDING_DIRECTORY, cat1, EMBEDDINGS_FILENAME), index_col=0)
    cat2_embeds_df = pd.read_csv(os.path.join(dataset_dir, EMBEDDING_DIRECTORY, cat2, EMBEDDINGS_FILENAME), index_col=0)

    dists = cdist(cat1_embeds_df.values, cat2_embeds_df.values, metric=metric)
    dists_df = pd.DataFrame(dists, columns=cat2_embeds_df.index, index=cat1_embeds_df.index).reset_index().rename(columns={'index': 'cat1_filepath'})

    dists_df = pd.melt(dists_df, id_vars=['cat1_filepath'], value_vars=cat2_embeds_df.index, var_name='cat2_filepath', value_name='distance')
    return dists_df[dists_df.distance <= cutoff]


def main():
    parser = argparse.ArgumentParser(description="Finds similar image pairs",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("--dataset_directory", type=str, required=True,
                        help="Path to the directory where the dataset is saved")
    parser.add_argument("--max_distance", type=float, required=False, default=5.0,
                        help="The cutoff above which images are not similar")
    parser.add_argument("--dist_metric", type=str, required=False, default='euclidean',
                        help="The distance metric used to compute similar images")

    args = parser.parse_args()

    dataset_dir = args.dataset_directory

    categories = get_categories(dataset_dir)

    print(f'Found categories: {categories}')

    os.makedirs(os.path.join(dataset_dir, SIMILAR_IMAGES_DIRECTORY), exist_ok=True)

    for cat1 in categories:
        for cat2 in categories:
            if cat1 >= cat2:
                continue

            print(f'Computing similar images for categories {cat1} and {cat2}')
            similar_imgs_df = get_similar_images(dataset_dir, cat1, cat2, args.dist_metric, args.max_distance)
            similar_imgs_df.to_csv(os.path.join(dataset_dir, SIMILAR_IMAGES_DIRECTORY, f'{SIMILAR_IMAGES_FILENAME}_{cat1}_{cat2}.csv'), index=False)


if __name__ == '__main__':
    main()
