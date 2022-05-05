print("########## IMPORTS ##########")
import numpy as np
import argparse
import time, os, sys, argparse, shutil, glob
import Cellpose3D_py

from Cellpose3D_py.utils.h5_converter import prepare_images, prepare_masks
from Cellpose3D_py.utils.csv_generator import create_csv
from Cellpose3D_py.models import UNet3D_cellpose
# from cellpose import utils, io, models
from pathlib import Path
print("Done")
print("\n")


print("########## PARAMETERS ##########")
# CELLPOSE 3D parameters
parser = argparse.ArgumentParser()

## input file -i
parser.add_argument('--infile', type = argparse.FileType('r'), help = 'Cellpose input image')
parser.add_argument('--mask', type = argparse.FileType('r'), help = 'mask from Cellpose')

## output settings
output_args = parser.add_argument_group("output arguments")
output_args.add_argument('--out', help = 'output tif mask')


args = parser.parse_args()

infile = args.infile.name
mask = args.mask.name
csv_out = args.out

print("Done")
print("\n")


print("########## DATA WORK ##########")
prepare_images(data_path = infile)
prepare_masks(data_path = mask)

exp = (infile, mask)

data_List = []
data_List.append(exp)
print(data_List)

create_csv(data_list = data_List, save_path = csv_out)

print("Done")
print("\n")