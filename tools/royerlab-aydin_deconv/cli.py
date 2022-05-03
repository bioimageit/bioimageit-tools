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
from aydin.restoration.deconvolve.lr import LucyRichardson
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

# AYDIN deconv parameters
parser = argparse.ArgumentParser()

parser.add_argument('--infile', type = argparse.FileType('r'), help = 'Aydin parameters')
parser.add_argument('--psf', type = argparse.FileType('r'), help = 'PSF image')
parser.add_argument('--slicing', type = str, default = "")
parser.add_argument('--backend', default=None, help='')
parser.add_argument('--out', help = 'deconvolved tif image')

args = parser.parse_args()


input_file_path = imread(args.infile.name)[0]
psf_path = args.psf.name
args_slicing = None
args_backend = None

if args.slicing == "${slicing}":
    args_slicing = None
if args.backend == "${backend}":
    args_backend = None


print("Done")
print("\n")



print("########## DECONVOLUTION ##########")

def lucyrichardson(files, psf_path):
    """lucyrichardson command

    Parameters
    ----------
    files
    psf_kernel

    """

    psf_kernel = imread(psf_path)[0]
    psf_kernel = psf_kernel.astype(numpy.float32, copy=False)
    psf_kernel /= psf_kernel.sum()

    lr = LucyRichardson(
        psf_kernel=psf_kernel, max_num_iterations=20, backend=args_backend
    )

    lr.train(files, files)
    deconvolved = lr.deconvolve(files)

    path = args.out
        
    imwrite(deconvolved, path)




lucyrichardson(input_file_path, psf_path)

print("Done")