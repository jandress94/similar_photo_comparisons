#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# compare_images.py
# Author: Jim Andress
# Created: 2020-12-29

import argparse
import os
import pandas as pd
import random
import tkinter as tk
from PIL import ImageTk, Image

from similar_photo_comparisons.constants import SIMILAR_IMAGES_DIRECTORY, RANKINGS_DIRECTORY, RANKINGS_FILENAME


def resize_img(img, max_width=600):
    if img.width > max_width:
        return img.resize((max_width, int(img.height * max_width / img.width)))


class ImgRankerGUI(tk.Frame):
    def __init__(self, imgs_to_rank_df, dataset_dir, master=None):
        super().__init__(master)
        self.master = master
        self.pack()

        self.imgs_to_rank_df = imgs_to_rank_df
        self.current_idx = 0
        self.is_flipped = False

        self.dataset_dir = dataset_dir

        self.create_widgets()
        self.refresh_imgs()

        self.rankings = []

    @property
    def current_row(self):
        return self.imgs_to_rank_df.loc[self.current_idx]

    def create_widgets(self):
        self.photo1 = ImageTk.PhotoImage(Image.open(self.current_row.cat1_filepath))
        self.button1 = tk.Button(self.master, image=self.photo1, command=self.press_button1)
        self.button1.pack(side='left')

        self.button_center = tk.Button(self.master, text='skip', command=self.skip)
        self.button_center.pack(side='left')

        self.photo2 = ImageTk.PhotoImage(Image.open(self.current_row.cat2_filepath))
        self.button2 = tk.Button(self.master, image=self.photo2, command=self.press_button2)
        self.button2.pack(side='left')

        self.button_save = tk.Button(self.master, text='save', command=self.save)
        self.button_save.pack(side='bottom')

    def refresh_imgs(self):
        self.is_flipped = random.random() < 0.5

        if not self.is_flipped:
            img_path1 = self.current_row.cat1_filepath
            img_path2 = self.current_row.cat2_filepath
        else:
            img_path1 = self.current_row.cat2_filepath
            img_path2 = self.current_row.cat1_filepath

        self.photo1 = ImageTk.PhotoImage(resize_img(Image.open(img_path1)))
        self.photo2 = ImageTk.PhotoImage(resize_img(Image.open(img_path2)))

        self.button1.configure(image=self.photo1)
        self.button2.configure(image=self.photo2)

    def skip(self):
        print('skipping')
        self.press_button(skipped=True)

    def press_button1(self):
        print('button1')
        if not self.is_flipped:
            self.press_button('cat1')
        else:
            self.press_button('cat2')

    def press_button2(self):
        print('button2')
        if not self.is_flipped:
            self.press_button('cat2')
        else:
            self.press_button('cat1')

    def press_button(self, success_category=None, skipped=False):
        if skipped:
            print('you skipped')
        else:
            print(f'you liked category {self.imgs_to_rank_df.loc[self.current_idx][success_category]}')

        self.rankings.append([
            self.current_row['cat1'],
            self.current_row['cat2'],
            self.current_row[f'cat1_filepath'],
            self.current_row[f'cat2_filepath'],
            self.current_row[success_category] if not skipped else None,
            skipped
        ])

        self.current_idx += 1
        if self.current_idx >= len(self.imgs_to_rank_df):
            self.close()
            return

        self.refresh_imgs()

    def save(self):
        print('saving')

        new_rankings_df = pd.DataFrame(self.rankings, columns=['cat1', 'cat2', 'cat1_filepath', 'cat2_filepath', 'liked_category', 'is_skipped'])

        ranking_filepath = os.path.join(self.dataset_dir, RANKINGS_DIRECTORY, RANKINGS_FILENAME)
        if os.path.exists(ranking_filepath):
            old_rankings = pd.read_csv(ranking_filepath)

            new_rankings_df = pd.concat([old_rankings, new_rankings_df], axis=0, ignore_index=True)

        new_rankings_df.to_csv(ranking_filepath, index=False)
        self.rankings = []

    def close(self):
        print('closing')
        self.save()

        self.master.destroy()


def get_imgs_to_rank(dataset_dir):
    similar_imgs_directory = os.path.join(dataset_dir, SIMILAR_IMAGES_DIRECTORY)

    similar_img_files = os.listdir(similar_imgs_directory)

    dfs = []
    for sim_img_file in similar_img_files:
        dfs.append(pd.read_csv(os.path.join(similar_imgs_directory, sim_img_file)))

    similar_imgs_df = pd.concat(dfs, axis=0, ignore_index=True)

    rankings_directory = os.path.join(dataset_dir, RANKINGS_DIRECTORY)
    os.makedirs(rankings_directory, exist_ok=True)

    rankings_filepath = os.path.join(rankings_directory, RANKINGS_FILENAME)
    if os.path.exists(rankings_filepath):
        completed_rankings = pd.read_csv(rankings_filepath)

        for _, row in completed_rankings.iterrows():
            similar_imgs_df = similar_imgs_df[((similar_imgs_df.cat1_filepath != row.cat1_filepath) | (similar_imgs_df.cat2_filepath != row.cat2_filepath)) &
                                              ((similar_imgs_df.cat1_filepath != row.cat2_filepath) | (similar_imgs_df.cat2_filepath != row.cat1_filepath))]

    return similar_imgs_df.sample(frac=1).reset_index(drop=True)


def main():
    parser = argparse.ArgumentParser(description="Compares the pairs of photos",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("--dataset_directory", type=str, required=True,
                        help="Path to the directory where the dataset is saved")

    args = parser.parse_args()

    dataset_dir = args.dataset_directory

    imgs_to_rank_df = get_imgs_to_rank(dataset_dir)

    if len(imgs_to_rank_df) > 0:
        root = tk.Tk()
        app = ImgRankerGUI(imgs_to_rank_df, dataset_dir, master=root)
        app.mainloop()
    else:
        print('all image pairs ranked')


if __name__ == '__main__':
    main()
