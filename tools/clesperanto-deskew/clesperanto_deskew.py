print("########## IMPORTS ##########")

import pyclesperanto_prototype as cle
import argparse

from skimage.io import imread, imsave, imshow

cle.get_device()


print("Done")
print("\n")


print("########## PARAMETERS ##########")

parser = argparse.ArgumentParser()

parser.add_argument('--infile', 
    type = argparse.FileType('r'), 
    help = 'Clesperanto parameters'
    )
parser.add_argument('--angle', 
    type = float, 
    help = 'Deskewing angle in degrees'
    )
parser.add_argument('--sigma_outline', 
    type = float, 
    help = 'sigma_outline'
    )
parser.add_argument('--voxel_size_x', 
    type = float, 
    help = 'voxel_size_x_in_microns'
    )
parser.add_argument('--voxel_size_y', 
    type = float, 
    help = 'voxel_size_y_in_microns'
    )
parser.add_argument('--voxel_size_z', 
    type = float, 
    help = 'voxel_size_z_in_microns'
    )
parser.add_argument('--out', 
    help = 'output csv'
    )
args = parser.parse_args()


input_image = args.infile.name
voxel_size_x_in_microns = args.voxel_size_x
voxel_size_y_in_microns = args.voxel_size_y
voxel_size_z_in_microns = args.voxel_size_z
deskewing_angle_in_degrees = args.angle
output = args.out

original_image = imread(input_image)
print("Input image : {}".format(original_image))
print("Loaded image size : " + str(original_image.shape))
input_to_GPU = cle.push(original_image)
print("Image size in GPU : " + str(input_to_GPU.shape))


print("Done")
print("\n")




print("########## IMAGE PROCESSING ##########")

deskewed = cle.deskew_y(input_to_GPU, 
                        angle_in_degrees=deskewing_angle_in_degrees, 
                        voxel_size_x=voxel_size_x_in_microns, 
                        voxel_size_y=voxel_size_y_in_microns, 
                        voxel_size_z=voxel_size_z_in_microns)


print("Done")
print("\n")



print("########## OUTPUT TIFF ##########")

imsave(output, deskewed)


print("Job done.")