print("########## IMPORTS ##########")

import ast
import os
import shutil
import sys
from copy import deepcopy
from glob import glob
import argparse
import numpy
from skimage.metrics import peak_signal_noise_ratio
from skimage.metrics import structural_similarity

from aydin.io.datasets import normalise
from aydin.it.base import ImageTranslatorBase
from aydin.io.io import imwrite, imread
from aydin.io.utils import get_output_image_path, get_save_model_path
from aydin.restoration.denoise.util.denoise_utils import get_denoiser_class_instance
from aydin.util.misc.json import load_any_json
from aydin.util.log.log import lprint, Log
from aydin.util.misc.slicing_helper import apply_slicing
from aydin import __version__
print("Done")
print("\n")


print("########## PARAMETERS ##########")

# AYDIN denoised parameters
parser = argparse.ArgumentParser()

parser.add_argument('--infile', type = argparse.FileType('r'), help = 'Aydin parameters')
parser.add_argument('--training-slicing', type = str, default = "")
parser.add_argument('--inference-slicing', type = str, default = '')
parser.add_argument('--batch-axes', type=str, help='only pass while denoising a single image')
parser.add_argument('--channel-axes', type=str, help='only pass while denoising a single image')
parser.add_argument('--variant', default='noise2selffgr-cb', type=str)
parser.add_argument('--out', help = 'denoised tif image')

args = parser.parse_args()

print("Done")
print("\n")

input_file_path = args.infile.name


args_training_slicing = ""
args_inference_slicing = ''
if args.batch_axes == "${batch-axes}":
    args_batch_axes = None
if args.channel_axes == "${channel-axes}":
    args_channel_axes = None


print("########## DENOISING ##########")

def denoise(files):
    """
    denoise command
    """

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
            lower_level_args=lower_level_args, variant=backend
        )

        denoiser.train(
            noisy2train,
            batch_axes=noisy_metadata.batch_axes
            if noisy_metadata is not None
            else None,
            chan_axes=noisy_metadata.channel_axes
            if noisy_metadata is not None
            else None,
            image_path=path,
        )

        denoised = denoiser.denoise(
            noisy2infer,
            batch_axes=noisy_metadata.batch_axes
            if noisy_metadata is not None
            else None,
            chan_axes=noisy_metadata.channel_axes
            if noisy_metadata is not None
            else None,
        )

        imwrite(denoised, output_path)
        lprint("DONE")



denoise(input_file_path)

print("Done")