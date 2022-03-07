import numpy as np
import time, os, sys, argparse, shutil, glob
from cellpose import utils, io, models
from pathlib import Path
print("Imports done")


# Paths
user_path = str(Path.home())
bioimageit_path = os.path.join(user_path, "BioImageIT")
workspace = os.path.join(bioimageit_path, "workspace")

print("WORKSPACE PATH : " + workspace)

os.chdir(workspace)
print("CURRENT DIRECTORY : " + os.getcwd())



# Cellpose_temp directory creation
if not os.path.exists("cellpose_temp") :
    os.mkdir("cellpose_temp")

cellpose_temp = os.path.join(workspace, "cellpose_temp")
os.chdir(cellpose_temp)

print("Moving to Cellpose temp dir : " + cellpose_temp)
print("CURRENT DIRECTORY : " + os.getcwd())


# CELLPOSE parameters
parser = argparse.ArgumentParser()
hardware_args = parser.add_argument_group("hardware arguments")

## input file -i
parser.add_argument('--infile', type = argparse.FileType('r'), help = 'Cellpose parameters')
hardware_args.add_argument('--use_gpu', required=False, default='True', type=str, help='use gpu if torch or mxnet with cuda installed')
parser.add_argument('--diameter', type = float, default = "0")
parser.add_argument('--auto_diam', type = str, default = 'False', help = 'Automated estimation of the diameter')
parser.add_argument('--channels', type = str, default = '[0,0]', help = '[0,0] IF YOU HAVE GRAYSCALE, [2,3] IF YOU HAVE G=cytoplasm and B=nucleus, [2,1] IF YOU HAVE G=cytoplasm and R=nucleus')

# settings for locating and formatting images
input_img_args = parser.add_argument_group("input image arguments")
input_img_args.add_argument('--dir',
                        default=cellpose_temp, type=str, help='folder containing data to run or train on.')

## model settings 
model_args = parser.add_argument_group("model arguments")
parser.add_argument('--pretrained_model', required=False, default='cyto', type=str, help='model to use')

## output settings
output_args = parser.add_argument_group("output arguments")
output_args.add_argument('--savedir',
                        default=cellpose_temp, type=str, help='folder to which segmentation results will be saved (defaults to input image directory)')
output_args.add_argument('--save_txt', action='store_true', help='flag to enable txt outlines for ImageJ (disabled by default)')
output_args.add_argument('--out', help = 'output tif mask')


args = parser.parse_args()
diam = 0

if args.auto_diam == "False" :
    diam = args.diameter
elif args.auto_diam == "True" :
    diam = None

chan = []
if args.channels == "[0,0]":
    chan = [0,0]
    print("GRAYSCALE")
elif args.channels == "[2,3]":
    chan = [2,3]
    print("GB")
elif args.channels == "[2,1]":
    chan = [2,1]
    print("GR")



print("Automated estimation of diameter : {}".format(args.auto_diam))
print("diameter = {}".format(diam))
print("GPU usage : {}".format(args.use_gpu))
print("PRETRANED MODEL : {}".format(args.pretrained_model))


input_file_path = args.infile.name
print("Input file path : {}".format(input_file_path))
input_dirname = os.path.dirname(input_file_path)
print("Input dirname : {}".format(input_dirname))
input_file_name = input_file_path.replace(input_dirname, "")
input_file_name = input_file_name[1:len(input_file_name)]
print("Input file name : {}".format(input_file_name))
print("Channels : {}".format(args.channels))


## Copy/paste -i to cellpose_temp directory
original_i = input_file_path
target_i = os.path.join(cellpose_temp, input_file_name)

shutil.copyfile(original_i, target_i)

## REPLACE FILES WITH YOUR IMAGE PATHS
files = [input_file_path]



# RUN CELLPOSE
# DEFINE CELLPOSE MODEL
# model_type='cyto' or model_type='nuclei'
model = models.Cellpose(gpu=args.use_gpu, model_type=args.pretrained_model)

# define CHANNELS to run segementation on
# grayscale=0, R=1, G=2, B=3
# channels = [cytoplasm, nucleus]
# if NUCLEUS channel does not exist, set the second channel to 0
# channels = [0,0]
# IF ALL YOUR IMAGES ARE THE SAME TYPE, you can give a list with 2 elements
# channels = [0,0] # IF YOU HAVE GRAYSCALE
# channels = [2,3] # IF YOU HAVE G=cytoplasm and B=nucleus
# channels = [2,1] # IF YOU HAVE G=cytoplasm and R=nucleus

# or if you have different types of channels in each image
channels = [chan]

# if diameter is set to None, the size of the cells is estimated on a per image basis
# you can set the average cell `diameter` in pixels yourself (recommended) 
# diameter can be a list or a single number for all images

# you can run all in a list e.g.
# >>> imgs = [io.imread(filename) in for filename in files]
# >>> masks, flows, styles, diams = model.eval(imgs, diameter=None, channels=channels)
# >>> io.masks_flows_to_seg(imgs, masks, flows, diams, files, channels)
# >>> io.save_to_png(imgs, masks, flows, files)

# or in a loop
print("Saving seg and tif...")
for chan, filename in zip(channels, files):
    img = io.imread(filename)
    masks, flows, styles, diams = model.eval(img, diameter = diam, channels = chan)

    # save results so you can load in gui
    # io.masks_flows_to_seg(img, masks, flows, diams, args.out, chan)

    # save results as png
    io.save_masks(img, masks, flows, args.out, png = False, tif = True) 



print("JOB DONE !")