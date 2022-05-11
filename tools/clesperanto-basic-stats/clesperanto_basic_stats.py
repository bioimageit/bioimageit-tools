print("########## IMPORTS ##########")

import pyclesperanto_prototype as cle
import numpy as np
import pandas as pd
import argparse, csv

from skimage.io import imread, imsave, imshow
from itertools import zip_longest

print("Done")
print("\n")


print("########## PARAMETERS ##########")

parser = argparse.ArgumentParser()

parser.add_argument('--infile', 
    type = argparse.FileType('r'), 
    help = 'Clesperanto parameters'
    )
parser.add_argument('--spot_sigma', 
    type = float, 
    help = 'spot sigma'
    )
parser.add_argument('--out', 
    help = 'output csv'
    )
args = parser.parse_args()


image = imread(args.infile.name)
spot_sigma = args.spot_sigma
output = args.out

print("Input image : {}".format(args.infile.name))
print("Loaded image size : " + str(image.shape))
input_to_GPU = cle.push(image)
print("Image size in GPU : " + str(input_to_GPU.shape))


print("Done")
print("\n")




print("########## IMAGE PROCESSING ##########")

labels = cle.voronoi_otsu_labeling(input_to_GPU, spot_sigma=spot_sigma)
statistics = cle.statistics_of_labelled_pixels(input_to_GPU, labels)

label = statistics["label"]
original_label = statistics["original_label"]
bbox_min_x = statistics["bbox_min_x"]
bbox_min_y = statistics["bbox_min_y"]
bbox_min_z = statistics["bbox_min_z"]
bbox_max_x = statistics["bbox_max_x"]
bbox_max_y = statistics["bbox_max_y"]
bbox_max_z = statistics["bbox_max_z"]
bbox_width = statistics["bbox_width"]
bbox_depth = statistics["bbox_depth"]
bbox_height = statistics["bbox_height"]
min_intensity = statistics["min_intensity"]
max_intensity = statistics["max_intensity"]
sum_intensity = statistics["sum_intensity"]
area = statistics["area"]
mean_intensity = statistics["mean_intensity"]
sum_intensity_times_x = statistics["sum_intensity_times_x"]
mass_center_x = statistics["mass_center_x"]
sum_intensity_times_y = statistics["sum_intensity_times_y"]
mass_center_y = statistics["mass_center_y"]
sum_intensity_times_z = statistics["sum_intensity_times_z"]
mass_center_z = statistics["mass_center_z"]
sum_x = statistics["sum_x"]
centroid_x = statistics["centroid_x"]
sum_y = statistics["sum_y"]
centroid_y = statistics["centroid_y"]
sum_z = statistics["sum_z"]
centroid_z = statistics["centroid_z"]
sum_distance_to_centroid = statistics["sum_distance_to_centroid"]
mean_distance_to_centroid = statistics["mean_distance_to_centroid"]
sum_distance_to_mass_center = statistics["sum_distance_to_mass_center"]
mean_distance_to_mass_center = statistics["mean_distance_to_mass_center"]
standard_deviation_intensity = statistics["standard_deviation_intensity"]
max_distance_to_centroid = statistics["max_distance_to_centroid"]
max_distance_to_mass_center = statistics["max_distance_to_mass_center"]
mean_max_distance_to_centroid_ratio = statistics["mean_max_distance_to_centroid_ratio"]
mean_max_distance_to_mass_center_ratio = statistics["mean_max_distance_to_mass_center_ratio"]


print("label : {}".format(label))

print("Done")
print("\n")



print("########## OUTPUT CSV ##########")

header = [label,
    original_label,
    bbox_min_x,
    bbox_min_y,
    bbox_min_z,
    bbox_max_x,
    bbox_max_y,
    bbox_max_z,
    bbox_width,
    bbox_height,
    bbox_depth,
    min_intensity,
    max_intensity,
    sum_intensity,
    area,
    mean_intensity,
    sum_intensity_times_x,
    mass_center_x,
    sum_intensity_times_y,
    mass_center_y,
    sum_intensity_times_z,
    mass_center_z,
    sum_x,
    centroid_x,
    sum_y,
    centroid_y,
    sum_z,
    centroid_z,
    sum_distance_to_centroid,
    mean_distance_to_centroid,
    sum_distance_to_mass_center,
    mean_distance_to_mass_center,
    standard_deviation_intensity,
    max_distance_to_centroid,
    max_distance_to_mass_center,
    mean_max_distance_to_centroid_ratio,
    mean_max_distance_to_mass_center_ratio
    ]

export_data = zip_longest(*header, fillvalue = '')

with open(output, "w", encoding="ISO-8859-1", newline='') as f:
    wr = csv.writer(f)
    wr.writerow(("label",
        "original_label",
        "bbox_min_x",
        "bbox_min_y",
        "bbox_min_z",
        "bbox_max_x",
        "bbox_max_y",
        "bbox_max_z",
        "bbox_width",
        "bbox_height",
        "bbox_depth",
        "min_intensity",
        "max_intensity",
        "sum_intensity",
        "area",
        "mean_intensity",
        "sum_intensity_times_x",
        "mass_center_x",
        "sum_intensity_times_y",
        "mass_center_y",
        "sum_intensity_times_z",
        "mass_center_z",
        "sum_x",
        "centroid_x",
        "sum_y",
        "centroid_y",
        "sum_z",
        "centroid_z",
        "sum_distance_to_centroid",
        "mean_distance_to_centroid",
        "sum_distance_to_mass_center",
        "mean_distance_to_mass_center",
        "standard_deviation_intensity",
        "max_distance_to_centroid",
        "max_distance_to_mass_center",
        "mean_max_distance_to_centroid_ratio",
        "mean_max_distance_to_mass_center_ratio"))
    wr.writerows(export_data)
f.close()


print("Job done.")