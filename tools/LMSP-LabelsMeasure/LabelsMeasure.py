#!/usr/bin/python

print("########## IMPORTS ##########")

from datetime import time, tzinfo
from tempfile import NamedTemporaryFile
from os import listdir
from os.path import isfile, join
from skimage import io, data, util
from skimage.morphology import disk
from skimage.draw import ellipse
from skimage.measure import label, regionprops, regionprops_table
from skimage.transform import rotate
from pathlib import Path
from scipy.stats import skew, kurtosis

import numpy as np
import skimage
import time
import datetime
import math
import os
import re
import argparse
import csv
import pandas as pd



print("Done")
print("\n")

###########################################################
##########################  I/O ###########################
###########################################################

print("########## I/O ##########")

parser = argparse.ArgumentParser()
parser.add_argument('--original', type = argparse.FileType('r'), help = 'original image')
parser.add_argument('--label', type = argparse.FileType('r'), help = 'label image, from cellpose for instance')
parser.add_argument('--pixel', type = int, help = 'size of the pixel erosion')
parser.add_argument('--binary_map', required=True, default='False', type=str, help='If no labels in your black & white image')
parser.add_argument('--out', type = str)
args = parser.parse_args()

print("original & label in the command line")


# Setting orginal & label images
original = args.original.name
label_name = args.label.name
print("Original : {}".format(original))
print("Label : {}".format(label_name))

original_img = io.imread(original)
label_img = io.imread(label_name)

original_img = np.float32(original_img)
print("original shape = {}".format(original_img.shape))

if args.binary_map == "True":
    label_img = label(label_img)
    binary = "True"
else:
    binary = "False"
print("Binary = {}".format(binary))

print("Pixel erosion = {}".format(args.pixel))
label_img = skimage.morphology.erosion(label_img, disk(args.pixel))

original_dirname = os.path.dirname(original)
label_dirname = os.path.dirname(label_name)
print("Original image dirname : {}".format(original_dirname))
print("Label image dirname : {}".format(label_dirname))

print("Original & label selected")

print("\n")

###########################################################
#####################  work on regions ####################
###########################################################

print("########## Work on regions ##########")

regions = regionprops(label_img)
print("Regions created")


def stdDev(regionmask, intensity_image):
    return np.std(intensity_image[regionmask])

def skewness(regionmask, intensity_image):
    return skew(intensity_image[regionmask])


def kurt(regionmask, intensity_image):
    return kurtosis(intensity_image[regionmask], fisher = True)

def center_mass(intensity_image):
    return regions[0].centroid

print("\n")

###########################################################
###################### save csv ###########################
###########################################################

print("########## saveTable ##########")

props = regionprops_table(label_img, original_img, properties = ('area', 'intensity_mean', 'intensity_min', 'intensity_max', 'perimeter', 'centroid', 'bbox', 'feret_diameter_max', 'slice'), 
    extra_properties=(stdDev, skewness, kurt, center_mass))
table = pd.DataFrame(props)
print(table.head())


table.to_csv(args.out)
print("Table saved as {}".format(args.out))



print("\n")
print("Finished")