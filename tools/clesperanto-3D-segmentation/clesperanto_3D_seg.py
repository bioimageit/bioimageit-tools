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
parser.add_argument('--voxel_size_x', 
    type = float, 
    help = 'voxel_size_x'
    )
parser.add_argument('--voxel_size_y', 
    type = float, 
    help = 'voxel_size_y'
    )
parser.add_argument('--voxel_size_z', 
    type = float, 
    help = 'voxel_size_z'
    )
parser.add_argument('--radius_x', 
    type = float, 
    help = 'radius_x'
    )
parser.add_argument('--radius_y', 
    type = float, 
    help = 'radius_y'
    )
parser.add_argument('--radius_z', 
    type = float, 
    help = 'radius_z'
    )
parser.add_argument('--out', 
    help = 'output csv'
    )
args = parser.parse_args()


input_image = args.infile.name
voxel_size_x = args.voxel_size_x
voxel_size_y = args.voxel_size_y
voxel_size_z = args.voxel_size_z
sigma_outline = args.sigma_outline
sigma_spot_detection = args.sigma_spot_detection
radius_x = args.radius_x
radius_y = args.radius_y
radius_z = args.radius_z
output = args.out

image = imread(input_image)
print("Input image : {}".format(input_image))
print("Loaded image size : " + str(image.shape))
input_to_GPU = cle.push(image)
print("Image size in GPU : " + str(input_to_GPU.shape))


print("Done")
print("\n")




print("########## IMAGE PROCESSING ##########")

resampled = cle.create([int(input_to_GPU.shape[0] * voxel_size_z), int(input_to_GPU.shape[1] * voxel_size_y), int(input_to_GPU.shape[2] * voxel_size_x)])
cle.scale(input_to_GPU, resampled, factor_x=voxel_size_x, factor_y=voxel_size_y, factor_z=voxel_size_z, centered=False)

print("Resampled image size : " + str(resampled.shape))

equalized_intensities_stack = cle.create_like(resampled)
a_slice = cle.create([resampled.shape[1], resampled.shape[0]])
num_slices = resampled.shape[0]
mean_intensity_stack = cle.mean_of_all_pixels(resampled)
corrected_slice = None

for z in range(0, num_slices):
    # get a single slice out of the stack
    cle.copy_slice(resampled, a_slice, z)
    # measure its intensity
    mean_intensity_slice = cle.mean_of_all_pixels(a_slice)
    # correct the intensity
    correction_factor = mean_intensity_slice/mean_intensity_stack
    corrected_slice = cle.multiply_image_and_scalar(a_slice, corrected_slice, correction_factor)
    # copy slice back in a stack
    cle.copy_slice(corrected_slice, equalized_intensities_stack, z)

backgrund_subtracted = cle.top_hat_box(equalized_intensities_stack, radius_x=radius_x, radius_y=radius_x, radius_z=radius_x)

segmented = cle.voronoi_otsu_labeling(backgrund_subtracted, spot_sigma=sigma_spot_detection, outline_sigma=sigma_outline)



print("Done")
print("\n")



print("########## OUTPUT TIFF ##########")

imsave(output, segmented)

print("Job done.")