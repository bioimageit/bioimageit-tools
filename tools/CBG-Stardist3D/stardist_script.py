import subprocess
import sys

# def install(package):
#     subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# install("stardist")
# install("tensorflow")
# install("keras")



from stardist.models import StarDist3D 
from stardist.data import test_image_nuclei_2d
from stardist.plot import render_label
from csbdeep.utils import normalize
from skimage import io
import argparse
print("imports done")
print("\n")


print("Parsing args")
parser = argparse.ArgumentParser()
parser.add_argument('--image', type = argparse.FileType('r'), help = 'input image')
parser.add_argument('--model', required=True, default='3D_demo', type=str, help='Pretrained model')
parser.add_argument('--out', type = str)
args = parser.parse_args()
print("\n")

# # prints a list of available models 
# print("Available models : ")
# StarDist3D.from_pretrained() 
# print("\n")

# creates a pretrained model
model = StarDist3D.from_pretrained(args.model)
print("Chosen model : {}".format(args.model))
print("\n")


img = args.image.name
img = io.imread(img)
print("Selected image : {}".format(args.image.name)) 
print("\n")

labels, _ = model.predict_instances(normalize(img))

io.imsave(args.out, labels)