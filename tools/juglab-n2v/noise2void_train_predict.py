print("########## IMPORTS ##########")

import os
import sys
import getopt
import argparse

from n2v.models import N2VConfig, N2V
from n2v.internals.N2V_DataGenerator import N2V_DataGenerator
from csbdeep.io import save_tiff_imagej_compatible
from tifffile import imread

print("Done")


print("########## PARAMETERS ##########")

parser = argparse.ArgumentParser()

parser.add_argument('--inputfile', 
    type = argparse.FileType('r'), 
    help = 'n2v parameters'
    )
parser.add_argument('--patch_size_xy', 
    type = float, 
    help = 'patch size xy'
    )
parser.add_argument('--patch_size_z', 
    type = float, 
    help = 'patch size z'
    )
parser.add_argument('--epochs', 
    type = int, 
    help = 'epochs'
    )
parser.add_argument('--steps_per_epoch', 
    type = int, 
    help = 'steps_per_epoch'
    )
parser.add_argument('--batch_size', 
    type = int, 
    help = 'batch_size'
    )
parser.add_argument('--neighborhood_radius', 
    type = float, 
    help = 'neighborhood_radius'
    )
parser.add_argument('--outputfile', 
    help = 'output and denoised image'
    )
args = parser.parse_args()

args_inputfile = args.inputfile.name
args_outputfile = args.outputfile
args_patch_size_xy = args.patch_size_xy
args_patch_size_z = args.patch_size_z
args_epochs = args.epochs
args_steps_per_epoch = args.steps_per_epoch
args_batch_size = args.batch_size
args_neighborhood_radius = args.neighborhood_radius

print('inputfile:', args_inputfile)
print('outputfile:', args_outputfile)
print('patch_size_xy:', args_patch_size_xy)
print('patch_size_z:', args_patch_size_z)
print('epochs:', args_epochs)
print('steps_per_epoch:', args_steps_per_epoch)
print('batch_size:', args_batch_size)
print('neighborhood_radius:', args_neighborhood_radius)

print("Done")


print("########## DEFINITION OF FUNCTIONS ##########")

def noise2void_train(image_file, patch_size_xy, patch_size_z, epochs,
                     steps_per_epoch, batch_size, neighborhood_radius):

    # Load the image
    datagen = N2V_DataGenerator()
    imgs = datagen.load_imgs(files=[image_file], dims='ZYX')
    print(imgs[0].shape)

    # generate patches
    patch_shape = (32, 64, 64)
    patches = datagen.generate_patches_from_list(imgs[:1], shape=patch_shape)
    p_num = patches.shape[0]
    X = patches[:p_num]
    X_val = patches[p_num:]

    # configuration of the training
    config = N2VConfig(X, unet_kern_size=3,
                       train_steps_per_epoch=args_steps_per_epoch,
                       train_epochs=args_epochs, train_loss='mse', batch_norm=True,
                       train_batch_size=batch_size, n2v_perc_pix=0.198,
                       n2v_patch_shape=(int(args_patch_size_z), int(args_patch_size_xy), int(patch_size_xy)),
                       n2v_manipulator='uniform_withCP',
                       n2v_neighborhood_radius=args_neighborhood_radius)
    vars(config)

    # a name used to identify the model
    model_name = 'n2v_3D'
    # the base directory in which our model will live
    basedir = 'models'
    # We are now creating our network model.
    model = N2V(config=config, name=model_name, basedir=basedir)
    # train
    history = model.train(X, X_val)


def noise2void_predict(image_file, output_file):
    model_name = 'n2v_3D'
    basedir = 'models'
    model = N2V(config=None, name=model_name, basedir=basedir)

    img = imread(image_file)
    pred = model.predict(img, axes='ZYX', n_tiles=(2, 4, 4))
    save_tiff_imagej_compatible(output_file, pred, 'ZYX')


def main(image_file, patch_size_xy, patch_size_z, epochs, steps_per_epoch, batch_size, neighborhood_radius):
    inputfile = image_file
    outputfile = args_outputfile

    # run
    print('input file=', inputfile)
    if os.path.isfile(inputfile):
        noise2void_train(inputfile, patch_size_xy, patch_size_z, epochs,
                         steps_per_epoch, batch_size, neighborhood_radius)
        noise2void_predict(inputfile, outputfile)
    else:
        print("Error: input file does not exists")
        sys.exit(1)
    print('done')

print("Done")


print("########## WORKING ##########")

if __name__ == "__main__":
    main(args_inputfile, args_patch_size_xy, args_patch_size_z, args_epochs, args_steps_per_epoch, args_batch_size, args_neighborhood_radius)

print("Job done")