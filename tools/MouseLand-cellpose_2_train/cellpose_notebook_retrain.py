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
parser.add_argument('--train_dir', 
    type=str, 
    help='Full path of your train directory'
    )
parser.add_argument('--test_dir', 
    type=str, 
    help='Full path of your test directory'
    )
parser.add_argument('--n_epochs', 
    default = "100",
    type = int, 
    )
parser.add_argument('--auto_diam', 
    type = str, 
    default = 'False', 
    help = 'Automated estimation of the diameter'
    )
parser.add_argument('--chan', 
    type = str, 
    default = '0', 
    help = '0 GRAYSCALE, 3 BLUE, 2 GREEN, 1 RED'
    )
parser.add_argument('--chan2', 
    type = str, 
    default = '3', 
    help = '0 NONE, 3 BLUE, 2 GREEN, 1 RED'
    )
parser.add_argument("--learning_rate",
    type = float,
    default = "0.1",
    help = "Learning rate"
    )
parser.add_argument("--weight_decay",
    type = float,
    default = "0.0001",
    help = "Weight decay"
    )
parser.add_argument('--evaluate', 
    type = str, 
    default = 'No', 
    help = 'Evaluate on test data (optional). If you have test data, check performance'
    )
parser.add_argument('--model_name', 
    type = str, 
    default = 'default_name', 
    help = 'Choose a name for your new model'
    )


input_img_args = parser.add_argument_group("input image arguments")
input_img_args.add_argument('--dir',
    default=cellpose_temp,
    type=str, 
    help='folder containing data to run or train on.'
    )

model_args = parser.add_argument_group("model arguments")
parser.add_argument('--initial_model', 
    required=False, 
    default='cyto', 
    type=str, 
    help='model to retrain'
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


chan = []
if args.chan == "0":
    chan = 0
    print("chan GRAYSCALE")
elif args.chan == "3":
    chan = 3
    print("chan BLUE")
elif args.chan == "1":
    chan = 1
    print("chan RED")
elif args.chan == "2":
    chan = 2
    print("chan GREEN")


chan2 = []
if args.chan2 == "0":
    chan2 = 0
    print("chan2 NONE")
elif args.chan2 == "3":
    chan2 = 3
    print("chan2 BLUE")
elif args.chan2 == "1":
    chan2 = 1
    print("chan2 RED")
elif args.chan2 == "2":
    chan2 = 2
    print("chan2 GREEN")



initial_model = args.initial_model
model_name = args.model_name
n_epochs = args.n_epochs
learning_rate = args.learning_rate
weight_decay = args.weight_decay

train_dir = args.train_dir
test_dir = args.test_dir
train_files = natsorted(glob(os.path.join(train_dir, '*.tif')))
train_seg = natsorted(glob(os.path.join(train_dir, '*.npy')))
test_files = natsorted(glob(os.path.join(test_dir, '*.npy')))
test_seg = natsorted(glob(os.path.join(test_dir, '*.npy')))


print(f'>>> GPU activated ? {yn[use_GPU]}')
print("Pretrained model : {}".format(initial_model))
print("New model name : {}".format(model_name))
print("Channel : {}".format(chan))
print("Channel 2 : {}".format(chan2))
print("Output file : {}".format(args.out))
print("Train directory : {}".format(train_dir))
print("Test directory : {}".format(test_dir))

print("Done")
print("\n")



print("########## TRAIN NEW MODEL ##########")
os.chdir(workspace)

# start logger (to see training across epochs)
logger = io.logger_setup()

# DEFINE CELLPOSE MODEL (without size model)
model = models.CellposeModel(gpu=use_GPU, model_type=initial_model)

# set channels
channels = [chan, chan2]

# get files
output = io.load_train_test_data(train_dir, test_dir, mask_filter='_seg.npy')
train_data, train_labels, _, test_data, test_labels, _ = output

new_model_path = model.train(train_data, train_labels, 
                              test_data=test_data,
                              test_labels=test_labels,
                              channels=channels, 
                              save_path=workspace, 
                              n_epochs=n_epochs,
                              learning_rate=learning_rate, 
                              weight_decay=weight_decay, 
                              nimg_per_epoch=8,
                              model_name=model_name)

# diameter of labels in training images
diam_labels = model.diam_labels.copy()

print("Done")
print("\n")




if args.evaluate == 'Yes' :
    print("########## EVALUATE ON TEST DATA ##########")
    # get files (during training, test_data is transformed so we will load it again)
    output = io.load_train_test_data(test_dir, mask_filter='_seg.npy')
    test_data, test_labels = output[:2]

    # run model on test images
    masks = model.eval(test_data, 
                   channels=[chan, chan2],
                   diameter=diam_labels)[0]

    # check performance using ground truth labels
    ap = metrics.average_precision(test_labels, masks)[0]
    print('')
    print(f'>>> average precision at iou threshold 0.5 = {ap[:,0].mean():.3f}')



print("Done")
print("\n")

print("JOB DONE !")