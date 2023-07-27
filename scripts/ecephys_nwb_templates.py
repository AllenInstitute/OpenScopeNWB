import h5py

import requests
import pandas as pd
import numpy as np
import os
from pathlib import Path, PurePath
from typing import Any, Dict, List, Tuple
from PIL import Image
from pynwb import NWBHDF5IO
from pynwb.image import ImageSeries, IndexSeries, \
     Images, GrayscaleImage, RGBImage
from allensdk.brain_observatory.behavior.data_objects.stimuli.presentations \
    import \
    Presentations


if __name__ == "__main__":
    directory = (r'/allen/programs/mindscope/' +
                 'workgroups/openscope/tiff_stim_files/' +
                 'illusion')
    nwb_path = (r'/allen/programs/mindscope/workgroups/openscope/' +
                'openscopedata2022/1194644312/2023-05-24-20-16/' +
                'nwb_path/1194644312/copy/spike_times.nwb')
    with NWBHDF5IO(path=nwb_path, mode="r+", load_namespaces=True) as io:
        nwb_file = io.read()
        intervals = nwb_file.intervals
        for stim in intervals:
            # Loop through each folder in the directory
            for folder in os.listdir(directory):
                # Check if the folder name contains the stim
                new_stim = stim.replace("_presentations", "")
                if new_stim in folder:
                    # Loop through each file in the folder
                    image_list = []
                    idx = 0
                    for filename in os.listdir(os.path.join(
                                               directory, folder)):
                        rgb_image = False
                        # Check if the file is a TIFF image
                        if (filename.endswith(".tif") or
                                filename.endswith(".tiff")):
                            # If so, load the image using numpy
                            # and append the pixel values to the image list
                            image = np.array(Image.open(
                                os.path.join(directory, folder, filename)))
                            if len(image.shape) == 2:
                                x, y = image.shape
                            else:
                                print(image.shape)
                                print("COLORED IMAGE")
                                x, y, rgb = image.shape
                                rgb_image = True
                            for i in range(x):
                                for j in range(y):
                                    image_list.append(
                                        (len(image_list), i, j, image[i, j]))
                        data = Image.open(os.path.join(
                            directory, folder, filename))
                        data = np.array(data)
                        data_list = []
                        times = []
                        data_list.append(data)

                        print(data.shape)
                        movie_frames = ImageSeries(
                            name=stim + str(idx),
                            data=data_list,
                            unit="NA",
                            format="raw",
                            rate=60.0,
                            # timestamps=times,
                        )

                        if rgb_image is not True:
                            image = GrayscaleImage(
                                name=stim + str(idx),
                                data=data,
                                description="movie",
                            )
                        else:
                            image = RGBImage(
                                name=stim + str(idx),
                                data=data,
                                description="movie"
                            )
                        frame_list.append(image)

                        if filename == os.listdir(os.path.join(
                                                  directory, folder))[-1]:
                            movies = Images(
                                name=stim,
                                images=frame_list,
                                description="movie"
                            )
                            nwb_file.add_stimulus_template(movies)
                        idx += 1
        io.write(nwb_file)
