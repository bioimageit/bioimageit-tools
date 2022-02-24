#!/usr/bin/python

import os
import os.path
import shutil
from pathlib import Path
import argparse
import glob
import numpy as np
import time, os, sys
from urllib.parse import urlparse
import matplotlib.pyplot as plt
import matplotlib as mpl
from cellpose import utils, io
from cellpose import models, io


# Paths
user_path = str(Path.home())
bioimageit_path = os.path.join(user_path, "BioImageIT")
workspace = os.path.join(bioimageit_path, "workspace")

print("WORKSPACE PATH = " + workspace)

os.chdir(workspace)
print("CURRENT DIRECTORY = " + os.getcwd())



# Cellpose_temp directory creation
if not os.path.exists("cellpose_temp") :
    os.mkdir("cellpose_temp")

cellpose_temp = os.path.join(workspace, "cellpose_temp")
os.chdir(cellpose_temp)

print("Cellpose temp dir = " + cellpose_temp)
print("CURRENT DIRECTORY = " + os.getcwd())


# CELLPOSE parameters
parser = argparse.ArgumentParser()


# ## settings for CPU vs GPU
# hardware_args = parser.add_argument_group("hardware arguments")

# if hardware_args.add_argument('--use_gpu', action='store_true', help='use gpu if torch or mxnet with cuda installed'):
#     use_gpu = True
# else:
#     use_gpu = False

# hardware_args.add_argument('--check_mkl', action='store_true', help='check if mkl working')
# hardware_args.add_argument('--mkldnn', action='store_true', help='for mxnet, force MXNET_SUBGRAPH_BACKEND = "MKLDNN"')

# # settings for locating and formatting images
# input_img_args = parser.add_argument_group("input image arguments")
# input_img_args.add_argument('--dir',
#                         default=cellpose_temp, type=str, help='folder containing data to run or train on.')
# input_img_args.add_argument('--look_one_level_down', action='store_true', help='run processing on all subdirectories of current folder')
# input_img_args.add_argument('--mxnet', action='store_true', help='use mxnet')
# input_img_args.add_argument('--img_filter',
#                         default=[], type=str, help='end string for images to run on')
# input_img_args.add_argument('--channel_axis',
#                         default=None, type=int, help='axis of image which corresponds to image channels')
# input_img_args.add_argument('--z_axis',
#                         default=None, type=int, help='axis of image which corresponds to Z dimension')
# input_img_args.add_argument('--chan',
#                         default=0, type=int, help='channel to segment; 0: GRAY, 1: RED, 2: GREEN, 3: BLUE. Default: %(default)s')
# input_img_args.add_argument('--chan2',
#                         default=0, type=int, help='nuclear channel (if cyto, optional); 0: NONE, 1: RED, 2: GREEN, 3: BLUE. Default: %(default)s')
# input_img_args.add_argument('--invert', action='store_true', help='invert grayscale channel')
# input_img_args.add_argument('--all_channels', action='store_true', help='use all channels in image if using own model and images with special channels')

# ## model settings 
# model_args = parser.add_argument_group("model arguments")
# parser.add_argument('--pretrained_model', required=False, default='cyto', type=str, help='model to use')
# parser.add_argument('--unet', required=False, default=0, type=int, help='run standard unet instead of cellpose flow output')
# model_args.add_argument('--nclasses',default=3, type=int, help='if running unet, choose 2 or 3; if training omni, choose 4; standard Cellpose uses 3')

# ## algorithm settings
# algorithm_args = parser.add_argument_group("algorithm arguments")
# parser.add_argument('--omni', action='store_true', help='Omnipose algorithm (disabled by default)')
# parser.add_argument('--cluster', action='store_true', help='DBSCAN clustering. Reduces oversegmentation of thin features (disabled by default).')
# parser.add_argument('--fast_mode', action='store_true', help='make code run faster by turning off 4 network averaging and resampling')
# parser.add_argument('--no_resample', action='store_true', help="disable dynamics on full image (makes algorithm faster for images with large diameters)")
# parser.add_argument('--no_net_avg', action='store_true', help='make code run faster by only running 1 network')
# parser.add_argument('--no_interp', action='store_true', help='do not interpolate when running dynamics (was default)')
# parser.add_argument('--do_3D', action='store_true', help='process images as 3D stacks of images (nplanes x nchan x Ly x Lx')
# parser.add_argument('--diameter', required=False, default=30., type=float, 
#                         help='cell diameter, if 0 cellpose will estimate for each image')
# parser.add_argument('--stitch_threshold', required=False, default=0.0, type=float, help='compute masks in 2D then stitch together masks with IoU>0.9 across planes')
    
# algorithm_args.add_argument('--flow_threshold', default=0.4, type=float, help='flow error threshold, 0 turns off this optional QC step. Default: %(default)s')
# algorithm_args.add_argument('--mask_threshold', default=0, type=float, help='mask threshold, default is 0, decrease to find more and larger masks')
    
# parser.add_argument('--anisotropy', required=False, default=1.0, type=float,
#                         help='anisotropy of volume in 3D')
# parser.add_argument('--diam_threshold', required=False, default=12.0, type=float, 
#                         help='cell diameter threshold for upscaling before mask rescontruction, default 12.')
# parser.add_argument('--exclude_on_edges', action='store_true', help='discard masks which touch edges of image')

# ## output settings
# output_args = parser.add_argument_group("output arguments")
# output_args.add_argument('--save_png', action='store_true', help='save masks as png and outlines as text file for ImageJ')
# output_args.add_argument('--save_tif', action='store_true', help='save masks as tif and outlines as text file for ImageJ')
# output_args.add_argument('--no_npy', action='store_true', help='suppress saving of npy')
# output_args.add_argument('--savedir',
#                         default=cellpose_temp, type=str, help='folder to which segmentation results will be saved (defaults to input image directory)')
# output_args.add_argument('--dir_above', action='store_true', help='save output folders adjacent to image folder instead of inside it (off by default)')
# output_args.add_argument('--in_folders', action='store_true', help='flag to save output in folders (off by default)')
# output_args.add_argument('--save_flows', action='store_true', help='whether or not to save RGB images of flows when masks are saved (disabled by default)')
# output_args.add_argument('--save_outlines', action='store_true', help='whether or not to save RGB outline images when masks are saved (disabled by default)')
# output_args.add_argument('--save_ncolor', action='store_true', help='whether or not to save minimal "n-color" masks (disabled by default')
# output_args.add_argument('--save_txt', action='store_true', help='flag to enable txt outlines for ImageJ (disabled by default)')

# ## training settings
# training_args = parser.add_argument_group("training arguments")
# training_args.add_argument('--train', action='store_true', help='train network using images in dir')
# training_args.add_argument('--train_size', action='store_true', help='train size network at end of training')
# training_args.add_argument('--mask_filter',
#                         default='_masks', type=str, help='end string for masks to run on. Default: %(default)s')
# training_args.add_argument('--test_dir',
#                         default=[], type=str, help='folder containing test data (optional)')
# training_args.add_argument('--learning_rate',
#                         default=0.2, type=float, help='learning rate. Default: %(default)s')
# training_args.add_argument('--n_epochs',
#                         default=500, type=int, help='number of epochs. Default: %(default)s')
# training_args.add_argument('--batch_size',
#                         default=8, type=int, help='batch size. Default: %(default)s')
# training_args.add_argument('--min_train_masks',
#                         default=5, type=int, help='minimum number of masks a training image must have to be used. Default: %(default)s')
# training_args.add_argument('--residual_on',
#                         default=1, type=int, help='use residual connections')
# training_args.add_argument('--style_on',
#                         default=1, type=int, help='use style vector')
# training_args.add_argument('--concatenation',
#                         default=0, type=int, help='concatenate downsampled layers with upsampled layers (off by default which means they are added)')
# training_args.add_argument('--save_every',
#                         default=100, type=int, help='number of epochs to skip between saves. Default: %(default)s')
# training_args.add_argument('--save_each', action='store_true', help='save the model under a different filename per --save_every epoch for later comparsion')

# ## misc settings
# parser.add_argument('--verbose', action='store_true', help='flag to output extra information (e.g. diameter metrics) for debugging and fine-tuning parameters')
# parser.add_argument('--testing', action='store_true', help='flag to suppress CLI user confirmation for saving output; for test scripts')

## input file -i
parser.add_argument('infile', type = argparse.FileType('r'), help = 'Cellpose parameters')
file_args = parser.parse_args()

input_file_path = file_args.infile.name
print("Input file path = {}".format(input_file_path))
input_dirname = os.path.dirname(input_file_path)
print("Input dirname = {}".format(input_dirname))
input_file_name = input_file_path.replace(input_dirname, "")
input_file_name = input_file_name[1:len(input_file_name)]
print("Input file name = {}".format(input_file_name))


# Copy/paste -i to cellpose_temp directory
original_i = input_file_path
target_i = os.path.join(cellpose_temp, input_file_name)

shutil.copyfile(original_i, target_i)


# Exec CELLPOSE
files = input_file_path
model = models.Cellpose(gpu = use_gpu, model_type = 'cyto')
channels = [[2,3], [0,0], [0,0]]

for chan, filename in zip(channels, files):
    img = io.imread(filename)
    masks, flows, styles, diams = model.eval(img, diameter=None, channels=chan)

    # save results so you can load in gui
    io.masks_flows_to_seg(img, masks, flows, diams, filename, chan)

    # save results as png
    io.save_to_png(img, masks, flows, filename)


# Copy/paste -o to original directory
output_mask_name = glob.glob(os.path.join(cellpose_temp ,"*_cp_masks*"), recursive = True)
original_o1 = str(output_mask_name)
original_o1 = original_o1[2:len(original_o1)-2]
target_o = input_dirname

print("Output masks = {}".format(original_o1))

for mask in output_mask_name :
    shutil.copy(mask, target_o)


# Remove cellpose_temp directory
os.chdir(workspace)
shutil.rmtree(cellpose_temp, ignore_errors=False, onerror=None)






















