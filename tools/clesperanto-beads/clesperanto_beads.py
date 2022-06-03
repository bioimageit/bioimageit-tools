print("########## IMPORTS ##########")

import pyclesperanto_prototype as cle
import numpy as np
import pandas as pd
import argparse, csv

from skimage.io import imread, imshow
from itertools import zip_longest


print("Done")
print("\n")


print("########## PARAMETERS ##########")

parser = argparse.ArgumentParser()

parser.add_argument('--infile', 
    type = argparse.FileType('r'), 
    help = 'Clesperanto parameters'
    )
parser.add_argument('--sigma', 
    type = float, 
    help = 'sigma'
    )
parser.add_argument('--scalar', 
    type = float, 
    help = 'scalar for thresholds'
    )
parser.add_argument('--out', 
    help = 'output csv'
    )
args = parser.parse_args()


input_image = args.infile.name
sigma = args.sigma
scalar = args.scalar
output = args.out

image = imread(input_image)
print("Input image : {}".format(input_image))
print("Loaded image size : " + str(image.shape))
input_to_GPU = cle.push(image)
print("Image size in GPU : " + str(input_to_GPU.shape))


print("Done")
print("\n")




print("########## IMAGE PROCESSING ##########")

# Local Maxima detection
maxima = cle.detect_maxima_box(input_to_GPU)

# Local threshold determination
labeled_maxima = cle.label_spots(maxima)
max_intensities = cle.read_intensities_from_map(labeled_maxima, input_to_GPU)
thresholds = cle.multiply_image_and_scalar(max_intensities, scalar=scalar)

# Make local threshold image
voronoi_label_image = cle.extend_labeling_via_voronoi(labeled_maxima)
threshold_image = cle.replace_intensities(voronoi_label_image, thresholds)
binary_segmented = cle.greater(input_to_GPU, threshold_image)

# Making bounding box
labels = cle.connected_components_labeling_box(binary_segmented)
stats = cle.statistics_of_labelled_pixels(label_image=labels)
print('Bounding box widths', stats['bbox_width'])
print('Bounding box heights', stats['bbox_height'])

bbox_width = stats['bbox_width']
bbox_height = stats['bbox_height']

header = [bbox_width, bbox_height]

print("Done")
print("\n")



print("########## OUTPUT CSV ##########")

export_data = zip_longest(*header, fillvalue = '')

with open(output, "w", encoding="ISO-8859-1", newline='') as f:
    wr = csv.writer(f)
    wr.writerow(("bbox_width", "bbox_height"))
    wr.writerows(export_data)
f.close()

print("Job done.")