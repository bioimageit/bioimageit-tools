print("########## IMPORTS ##########")

import pyclesperanto_prototype as cle
import numpy as np
import argparse

from skimage.io import imread, imsave, imshow

print("Done")
print("\n")


print("########## PARAMETERS ##########")

parser = argparse.ArgumentParser()

parser.add_argument('--infile', 
    type = argparse.FileType('r'), 
    help = 'Clesperanto parameters'
    )
parser.add_argument('--corrected_binary', 
    type = str, 
    help = 'if non corrected is not good'
    )
parser.add_argument('--radius_x', 
    type = float, 
    help = 'radius_x for corrected binary'
    )
parser.add_argument('--radius_y', 
    type = float, 
    help = 'radius_y for corrected binary'
    )
parser.add_argument('--out', 
    help = 'output csv'
    )
args = parser.parse_args()


input_image = args.infile.name
radius_x = args.radius_x
radius_y = args.radius_y
output = args.out

image = imread(input_image)
print("Input image : {}".format(input_image))
print("Loaded image size : " + str(image.shape))
input_to_GPU = cle.push(image)
print("Image size in GPU : " + str(input_to_GPU.shape))


print("Done")
print("\n")




print("########## IMAGE PROCESSING ##########")

binary = cle.binary_not(cle.threshold_otsu(input_to_GPU))
labels = cle.voronoi_labeling(binary)

if args.corrected_binary == "True" :
    corrected_binary = cle.maximum_box(cle.minimum_box(binary, radius_x=radius_x, radius_y=radius_y), radius_x=radius_x, radius_y=radius_y)
    labels = cle.voronoi_labeling(corrected_binary)


print("Done")
print("\n")



print("########## OUTPUT TIFF ##########")

imsave(output, labels)

print("Job done.")