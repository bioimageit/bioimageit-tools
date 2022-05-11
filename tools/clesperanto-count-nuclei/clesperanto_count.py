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

number_of_nuclei_b = nuclei_b.max()
number_of_nuclei_g = nuclei_g.max()
number_of_nuclei_r = nuclei_r.max()

print("Nuclei blue positive:", number_of_nuclei_b)
print("Nuclei green positive:", number_of_nuclei_g)
print("Nuclei red positive:", number_of_nuclei_r)

count_map_bg = cle.proximal_other_labels_count_map(nuclei_b, nuclei_g)
count_map_br = cle.proximal_other_labels_count_map(nuclei_b, nuclei_r)
count_map_gb = cle.proximal_other_labels_count_map(nuclei_g, nuclei_b)
count_map_gr = cle.proximal_other_labels_count_map(nuclei_g, nuclei_r)
count_map_rb = cle.proximal_other_labels_count_map(nuclei_r, nuclei_b)
count_map_rg = cle.proximal_other_labels_count_map(nuclei_r, nuclei_g)

print("\n")

double_positive_bg = cle.exclude_labels_with_map_values_out_of_range(
    count_map_bg, 
    nuclei_b, 
    minimum_value_range=1)
double_positive_br = cle.exclude_labels_with_map_values_out_of_range(
    count_map_br, 
    nuclei_b, 
    minimum_value_range=1)
double_positive_gb = cle.exclude_labels_with_map_values_out_of_range(
    count_map_gb, 
    nuclei_g, 
    minimum_value_range=1)
double_positive_gr = cle.exclude_labels_with_map_values_out_of_range(
    count_map_gr, 
    nuclei_g, 
    minimum_value_range=1)
double_positive_rb = cle.exclude_labels_with_map_values_out_of_range(
    count_map_rb, 
    nuclei_r, 
    minimum_value_range=1)
double_positive_rg = cle.exclude_labels_with_map_values_out_of_range(
    count_map_rg, 
    nuclei_r, 
    minimum_value_range=1)

number_of_double_bg = double_positive_bg.max()
number_of_double_br = double_positive_br.max()
number_of_double_gb = double_positive_gb.max()
number_of_double_gr = double_positive_gr.max()
number_of_double_rb = double_positive_rb.max()
number_of_double_rg = double_positive_rg.max()

print("Number of blue positives that also express green", number_of_double_bg)
print("Number of blue positives that also express red", number_of_double_br)
print("Number of green positives that also express blue", number_of_double_gb)
print("Number of green positives that also express red", number_of_double_gr)
print("Number of red positives that also express blue", number_of_double_rb)
print("Number of red positives that also express green", number_of_double_rg)

print("Done")
print("\n")



print("########## OUTPUT CSV ##########")

f = open(args.out, "w")
f.write("b = " + str(number_of_nuclei_b) + "\t")
f.write("g = " + str(number_of_nuclei_g) + "\t")
f.write("r = " + str(number_of_nuclei_r) + "\t")
f.write("bg = " + str(number_of_double_bg) + "\t")
f.write("br = " + str(number_of_double_br) + "\t")
f.write("gb = " + str(number_of_double_gb) + "\t")
f.write("gr = " + str(number_of_double_gr) + "\t")
f.write("rb = " + str(number_of_double_rb) + "\t")
f.write("rg = " + str(number_of_double_rg))

print("Job done.")