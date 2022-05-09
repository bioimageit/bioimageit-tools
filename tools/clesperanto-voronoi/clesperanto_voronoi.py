print("########## IMPORTS ##########")

import pyclesperanto_prototype as cle
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
parser.add_argument('--sigma_spot_detection', 
    type = float, 
    help = 'sigma_spot_detection'
    )
parser.add_argument('--sigma_outline', 
    type = float, 
    help = 'sigma_outline'
    )
parser.add_argument('--out', 
    help = 'output csv'
    )
args = parser.parse_args()


input_image = args.infile.name
input_sigma_detect = args.sigma_spot_detection
input_sigma_outline = args.sigma_outline
output = args.out

image = imread(input_image)
print("Input image : {}".format(input_image))
print("Loaded image size : " + str(image.shape))
input_to_GPU = cle.push(image)
print("Image size in GPU : " + str(input_to_GPU.shape))


print("Done")
print("\n")




print("########## IMAGE PROCESSING ##########")

segmented = cle.voronoi_otsu_labeling(input_to_GPU, spot_sigma=input_sigma_detect, outline_sigma=input_sigma_outline)

print("Done")
print("\n")



print("########## OUTPUT TIFF ##########")

imsave(output, segmented)

print("Job done.")