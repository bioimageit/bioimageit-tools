print("########## IMPORTS ##########")
import numpy as np
import time, os, sys, argparse, shutil, glob
from cellpose import utils, io, models, core, metrics
from pathlib import Path
from glob import glob
from natsort import natsorted
print("Done")
print("\n")




print("########## GPU ? ##########")
use_GPU = core.use_gpu()
yn = ['NO', 'YES']
print(f'>>> GPU activated? {yn[use_GPU]}')
print("Done")
print("\n")




print("########## PATHS (BioImageIT & workspace) ##########")
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
parser.add_argument('--diameter', 
    type = float, 
    default = "0",
    help = "diameter of cells (set to zero to use diameter from training set)",
    )
parser.add_argument('--chan', 
    type = str, 
    default = '0', 
    help = '0 GRAYSCALE, 3 BLUE, 2 GREEN, 1 RED'
    )
parser.add_argument('--chan2', 
    type = str, 
    default = '3', 
    help = '0 NONE, 3 BLUE, 2 GREEN, 1 RED ; If you have a secondary channel that can be used, for instance nuclei, choose it here'
    )
parser.add_argument('--model_path', 
    type = str, 
    default = 'model_path', 
    help = 'Custom model path (full path)'
    )
parser.add_argument('--flow_threshold', 
    type = float, 
    default = "0.4",
    help = "threshold on flow error to accept a mask (set higher to get more cells, e.g. in range from (0.1, 3.0), OR set to 0.0 to turn off so no cells discarded)",
    )
parser.add_argument('--cellprob_threshold', 
    type = float, 
    default = "0.4",
    help = "threshold on cellprob output to seed cell masks (set lower to include more pixels or higher to include fewer, e.g. in range from (-6, 6))",
    )


input_img_args = parser.add_argument_group("input image arguments")
input_img_args.add_argument('--dir',
    default=cellpose_temp,
    type=str, 
    help='Path to images'
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


model_path = args.model_path
input_file_path = args.infile.name
input_dirname = os.path.dirname(input_file_path)
input_file_name = input_file_path.replace(input_dirname, "")
input_file_name = input_file_name[1:len(input_file_name)]
diameter = args.diameter
flow_threshold = args.flow_threshold
cellprob_threshold = args.cellprob_threshold
chan = args.chan
chan2 = args.chan2


print("Custom model : {}".format(model_path))
print("Diameter : {}".format(diameter))
print("GPU usage : {}".format(use_GPU))
print("Channel 1 : {}".format(chan))
print("Channel 2 : {}".format(chan2))
print("Flow threshold : {}".format(flow_threshold))
print("Cellprob threshold : {}".format(cellprob_threshold))
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





print("########## RUN CUSTOM MODEL ##########")
os.chdir(workspace)

# gets image files in dir (ignoring image files ending in _masks)
files = io.get_image_files(cellpose_temp, '_masks')
print(files)
images = [io.imread(f) for f in files]

# declare model
model = models.CellposeModel(gpu=True, 
                             pretrained_model=model_path)

# use model diameter if user diameter is 0
diameter = model.diam_labels if diameter==0 else diameter

# run model on test images
masks, flows, styles = model.eval(images, 
                                  channels=[chan, chan2],
                                  diameter=diameter,
                                  flow_threshold=flow_threshold,
                                  cellprob_threshold=cellprob_threshold
                                  )

print("Done")
print("\n")




print("########## SAVE OUTPUT MASKS TO TIFFS ##########")
io.save_masks(images, 
              masks, 
              flows, 
              files, 
              channels=[chan, chan2],
              png=False, # save masks as PNGs and save example image
              tif=True, # save masks as TIFFs
              save_txt=False, # save txt outlines for ImageJ
              save_flows=False, # save flows as TIFFs
              save_outlines=False, # save outlines as TIFFs 
              )


print("Done")
print("\n")

print("JOB DONE !")