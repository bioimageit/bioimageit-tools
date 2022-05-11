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


raw_image = imread(args.infile.name)
blue_chan = raw_image[...,0]
green_chan = raw_image[...,1]
red_chan = raw_image[...,2]
spot_sigma = args.spot_sigma
output = args.out

print("Input image : {}".format(args.infile.name))
print("Loaded image size : " + str(raw_image.shape))
input_to_GPU = cle.push(raw_image)
print("Image size in GPU : " + str(input_to_GPU.shape))


print("Done")
print("\n")




print("########## IMAGE PROCESSING ##########")

nuclei_b = cle.voronoi_otsu_labeling(blue_chan, spot_sigma=spot_sigma)
nuclei_g = cle.voronoi_otsu_labeling(green_chan, spot_sigma=spot_sigma)
nuclei_r = cle.voronoi_otsu_labeling(red_chan, spot_sigma=spot_sigma)

intensity_map_bg = cle.mean_intensity_map(green_chan, nuclei_b)
intensity_map_br = cle.mean_intensity_map(red_chan, nuclei_b)
intensity_map_gb = cle.mean_intensity_map(blue_chan, nuclei_g)
intensity_map_gr = cle.mean_intensity_map(red_chan, nuclei_g)
intensity_map_rb = cle.mean_intensity_map(blue_chan, nuclei_r)
intensity_map_rg = cle.mean_intensity_map(green_chan, nuclei_r)

statistics_bg = cle.statistics_of_background_and_labelled_pixels(green_chan, nuclei_b)
statistics_br = cle.statistics_of_background_and_labelled_pixels(red_chan, nuclei_b)
statistics_gb = cle.statistics_of_background_and_labelled_pixels(blue_chan, nuclei_g)
statistics_gr = cle.statistics_of_background_and_labelled_pixels(red_chan, nuclei_g)
statistics_rb = cle.statistics_of_background_and_labelled_pixels(blue_chan, nuclei_r)
statistics_rg = cle.statistics_of_background_and_labelled_pixels(green_chan, nuclei_r)

intensity_vector_bg = statistics_bg["mean_intensity"]
intensity_vector_br = statistics_br["mean_intensity"]
intensity_vector_gb = statistics_gb["mean_intensity"]
intensity_vector_gr = statistics_gr["mean_intensity"]
intensity_vector_rb = statistics_rb["mean_intensity"]
intensity_vector_rg = statistics_rg["mean_intensity"]

print("intensity_vector_bg = {}".format(intensity_vector_bg))
print("intensity_vector_br = {}".format(intensity_vector_br))
print("intensity_vector_gb = {}".format(intensity_vector_gb))
print("intensity_vector_gr = {}".format(intensity_vector_gr))
print("intensity_vector_rb = {}".format(intensity_vector_rb))
print("intensity_vector_rg = {}".format(intensity_vector_bg))

print("Done")
print("\n")



print("########## OUTPUT CSV ##########")

header = [intensity_vector_bg,
    intensity_vector_br,
    intensity_vector_gb,
    intensity_vector_gr,
    intensity_vector_rb,
    intensity_vector_rg
    ]

export_data = zip_longest(*header, fillvalue = '')

with open(output, "w", encoding="ISO-8859-1", newline='') as f:
    wr = csv.writer(f)
    wr.writerow(("intensity_vector_bg","intensity_vector_br","intensity_vector_gb","intensity_vector_gr","intensity_vector_rb","intensity_vector_rg"))
    wr.writerows(export_data)
f.close()


print("Job done.")