print("########## IMPORTS ##########")

import pyclesperanto_prototype as cle
import numpy as np
import argparse, csv

from skimage.io import imread, imsave, imshow

print("Done")
print("\n")


print("########## PARAMETERS ##########")

parser = argparse.ArgumentParser()

parser.add_argument('--infile', 
    type = argparse.FileType('r'), 
    help = 'Clesperanto parameters'
    )
parser.add_argument('--sigma_x', 
    type = float, 
    help = 'Sigma x for guassian blur'
    )
parser.add_argument('--sigma_y', 
    type = float, 
    help = 'Sigma y for guassian blur'
    )
parser.add_argument('--out', 
    help = 'output csv'
    )
args = parser.parse_args()


input_image = args.infile.name
input_sigma_x = args.sigma_x
input_sigma_y = args.sigma_y


image = imread(input_image)
print("Input image : {}".format(input_image))
print("Loaded image size : " + str(image.shape))
input_to_GPU = cle.push(image)
print("Image size in GPU : " + str(input_to_GPU.shape))


print("Done")
print("\n")




print("########## IMAGE PROCESSING ##########")

blurred = cle.gaussian_blur(input_to_GPU, sigma_x = input_sigma_x, sigma_y = input_sigma_y)
binary = cle.threshold_otsu(blurred)
labeled = cle.connected_components_labeling_box(binary)


num_labels = cle.maximum_of_all_pixels(labeled)
print("Number of objects in the image: " + str(num_labels))

print("Done")
print("\n")



print("########## OUTPUT CSV ##########")

f = open(args.out, "w")
f.write(str(num_labels))

print("Job done.")