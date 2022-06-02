print("########## IMPORTS ##########")

import ast, numpy, os, shutil, sys, argparse, aydin

from copy import deepcopy
from glob import glob
from aydin.io.io import imwrite, imread
from aydin.util.misc.json import load_any_json
from aydin.util.misc.slicing_helper import apply_slicing
from aydin.io.datasets import normalise
from aydin.it.base import ImageTranslatorBase
from aydin.io.utils import get_output_image_path, get_save_model_path
from aydin.restoration.denoise.util.denoise_utils import get_denoiser_class_instance
from aydin.util.log.log import lprint, Log
from aydin.util.misc.slicing_helper import apply_slicing
from aydin import __version__



print("Done")
print("\n")


print("########## PARAMETERS ##########")

parser = argparse.ArgumentParser()

parser.add_argument('--infile', type = argparse.FileType('r'), help = 'Aydin parameters')
parser.add_argument('--training_slicing', type = str, default = "")
parser.add_argument('--inference_slicing', type = str, default = '')
parser.add_argument('--batch_axes', type = str, help = 'only pass while denoising a single image')
parser.add_argument('--channel_axes', type = str, help = 'only pass while denoising a single image')
parser.add_argument('--variant', default='noise2selffgr-cb', type = str)
parser.add_argument('--lower_level_args', default=None, type = str)
parser.add_argument('--model_path', default=None, type = str)
parser.add_argument('--out', help = 'denoised tif image')

args = parser.parse_args()

image = args.infile.name
# image = imread(image)

variant = args.variant
output = args.out

args_lower_level_args = args.lower_level_args
args_model_path = args.model_path

args_training_slicing = ""
args_inference_slicing = ""
if args.batch_axes == "default":
    args_batch_axes = None
if args.channel_axes == "default":
    args_channel_axes = None
if args.lower_level_args == "default":
    args_lower_level_args = None
if args.model_path == "default":
    args_model_path = None

print("Infile : ", image)

if args_lower_level_args != None :
    print("Reference parameters : lower level args JSON")
    print("Lower level args file : ", args_lower_level_args)
else :
    print("Lower level args file : ", args_lower_level_args)
    print("Reference parameters : command line args")
    print("Variant : ", args.variant)

print("Model path : ", args_model_path)


print("Done")
print("\n")



print("########## DENOISING ##########")

def denoise(files):
    """
    denoise command
    """

    # Check whether a path is provided for a model to use or save
    input_model_path = args_model_path if args_model_path else None
    print("INPUT MODEL PATH : ", input_model_path)

    # Check whether a filename is provided for lower-level-args json
    if args_lower_level_args:
        print("LOWER LEVEL ARGS : ", args_lower_level_args)
        lower_level_args = load_any_json(args_lower_level_args)
        backend = lower_level_args["variant"]
        print("BACKEND : ", backend)
    else:
        lower_level_args = None
        backend = args.variant


    filenames = []
    for filename in files:
        # if our shell does not do filename globbing
        expanded = list(glob(filename))

        filenames.extend(expanded)

    for filename in filenames:
        path = os.path.abspath(files)
        noisy, noisy_metadata = imread(path)

        noisy2train = apply_slicing(noisy, args_training_slicing)
        noisy2infer = apply_slicing(noisy, args_inference_slicing)

        if args.batch_axes is not None and len(files) == 1:
            noisy_metadata.batch_axes = ast.literal_eval(args_batch_axes)

        if args.channel_axes is not None and len(files) == 1:
            noisy_metadata.channel_axes = ast.literal_eval(args_channel_axes)

        output_path = args.out

        denoiser = get_denoiser_class_instance(
            lower_level_args = lower_level_args, variant = backend
        )

        denoiser.train(
            noisy2train,
            batch_axes = noisy_metadata.batch_axes
            if noisy_metadata is not None
            else None,
            chan_axes = noisy_metadata.channel_axes
            if noisy_metadata is not None
            else None,
            image_path = path,
        )

        denoised = denoiser.denoise(
            noisy2infer,
            batch_axes = noisy_metadata.batch_axes
            if noisy_metadata is not None
            else None,
            chan_axes = noisy_metadata.channel_axes
            if noisy_metadata is not None
            else None,
        )

        imwrite(denoised, output)
        lprint("DONE")



denoise(image)

print("Done")