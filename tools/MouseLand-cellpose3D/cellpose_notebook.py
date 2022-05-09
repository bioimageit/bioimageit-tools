print("########## IMPORTS ##########")
import numpy as np
import time, os, sys, argparse, shutil, glob
from cellpose import utils, io, models, core, metrics
from pathlib import Path
print("Done")
print("\n")


print("########## PATHS ##########")
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
print("Done")
print("\n")


print("########## PARAMETERS ##########")
parser = argparse.ArgumentParser()
hardware_args = parser.add_argument_group("hardware arguments")

parser.add_argument('--infile', 
    type = argparse.FileType('r'), 
    help = 'Cellpose parameters'
    )
hardware_args.add_argument('--use_gpu', 
    required=False, 
    default='True', 
    type=str, 
    help='use gpu if torch or mxnet with cuda installed'
    )
parser.add_argument('--diameter', 
    type = float, 
    default = "0"
    )
parser.add_argument('--auto_diam', 
    type = str, 
    default = 'False', 
    help = 'Automated estimation of the diameter'
    )
parser.add_argument('--channels', 
    type = str, 
    default = '[0,0]', 
    help = '[0,0] IF YOU HAVE GRAYSCALE, [2,3] IF YOU HAVE G=cytoplasm and B=nucleus, [2,1] IF YOU HAVE G=cytoplasm and R=nucleus'
    )
parser.add_argument('--do_three', 
    type = str, 
    default = 'False', 
    help = 'Cellpose in 3D'
    )


input_img_args = parser.add_argument_group("input image arguments")
input_img_args.add_argument('--dir',
    default=cellpose_temp,
    type=str, 
    help='folder containing data to run or train on.'
    )

model_args = parser.add_argument_group("model arguments")
parser.add_argument('--pretrained_model', 
    required=False, 
    default='cyto', 
    type=str, 
    help='model to use'
    )

output_args = parser.add_argument_group("output arguments")
output_args.add_argument('--savedir',
    default=cellpose_temp, 
    type=str, 
    help='folder to which segmentation results will be saved (defaults to input image directory)'
    )
output_args.add_argument('--save_txt', 
    action='store_true', 
    help='flag to enable txt outlines for ImageJ (disabled by default)'
    )
output_args.add_argument('--out', 
    help = 'output tif mask'
    )


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



initial_model = args.pretrained_model
input_file_path = args.infile.name
input_dirname = os.path.dirname(input_file_path)
input_file_name = input_file_path.replace(input_dirname, "")
input_file_name = input_file_name[1:len(input_file_name)]
use_GPU = args.use_gpu
do_3D = args.do_three



print("Automated estimation of diameter : {}".format(diam))
print("Diameter : {}".format(diam))
print("GPU usage : {}".format(use_GPU))
print("Pretrained model : {}".format(initial_model))
print("3D : {}".format(do_3D))
print("Channels : {}".format(chan))
print("Input file path : {}".format(input_file_path))
print("Input dirname : {}".format(input_dirname))
print("Input file name : {}".format(input_file_name))
print("Output file : {}".format(args.out))



## Copy/paste -i to cellpose_temp directory
original_i = input_file_path
target_i = os.path.join(cellpose_temp, input_file_name)

shutil.copyfile(original_i, target_i)

## REPLACE FILES WITH YOUR IMAGE PATHS
# files = [input_file_path]
# images = [io.imread(f) for f in files]
images = io.imread(input_file_path)

channels = [chan]

print("Done")
print("\n")


print("########## MODEL ##########")
model = models.CellposeModel(gpu = use_GPU, 
    model_type = initial_model
    )

print("Done")
print("\n")



print("########## RUN CELLPOSE ##########")
masks, flows, styles = model.eval(images, 
    diameter = diam, 
    channels = chan, 
    do_3D = do_3D
    )

print("Done")
print("\n")


print("########## SAVE MASK ##########")
io.save_masks(images, 
    masks, 
    flows, 
    args.out, 
    channels = chan, 
    png = False, 
    tif = True, 
    save_txt = False, 
    save_flows = False, 
    save_outlines = False
    )

print("Done")
print("\n")


os.chdir(workspace)

out_img_1 = args.out.replace(".tif", "_cp_masks.tif")

os.rename(out_img_1, args.out)

shutil.rmtree("cellpose_temp")

print("JOB DONE !")