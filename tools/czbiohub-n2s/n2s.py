print("########## IMPORTS ##########")

import sys, argparse, torch
import numpy as np

from noise2self.util import show, plot_images, plot_tensors
from skimage.morphology import disk
from skimage.filters import gaussian, median
from skimage import data, img_as_float, img_as_ubyte
from skimage.color import gray2rgb
from skimage.util import random_noise
from skimage.metrics import peak_signal_noise_ratio
from skimage.io import imread, imsave, imshow
from noise2self.util import getbestgpu
from noise2self.mask import Masker
from noise2self.models.dncnn import DnCNN
from noise2self.models.babyunet import BabyUnet
from noise2self.models.singleconv import SingleConvolution
from noise2self.models.unet import Unet
from torch.nn import MSELoss, L1Loss
from torch.optim import Adam

print("Done")
print("\n")



print("########## PARAMETERS ##########")

parser = argparse.ArgumentParser()

parser.add_argument('--infile', 
    type = argparse.FileType('r'), 
    help = 'Noised image'
    )
parser.add_argument('--model', 
    help = 'Model to use : BabyUnet, DnCNN, SingleConvolution or Unet'
    )
parser.add_argument('--num_of_layers', 
    type = int, 
    help = 'Number of layers in the convolutional network'
    )
parser.add_argument('--masker_width', 
    type = int, 
    help = 'Width of the mask'
    )
parser.add_argument('--iterations', 
    type = int, 
    help = 'Number of iterations during training'
    )
parser.add_argument('--out', 
    help = 'output denoised image'
    )
args = parser.parse_args()

input_image = args.infile.name
image = imread(input_image)
image = img_as_float(image)
num_of_layers = args.num_of_layers
masker_width = args.masker_width
iterations = args.iterations
output_image = args.out

print("Input image : ", input_image)
print("Image shape : ", image.shape)
print("Number of layers : ", num_of_layers)
print("Interations : ", iterations)

print("Done")
print("\n")



print("########## MASKING/MODEL ##########")

noisy = torch.Tensor(image[np.newaxis, np.newaxis])

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
masker = Masker(width = masker_width, mode='interpolate')

torch.manual_seed(3)

if args.model == "DnCNN":
	model = DnCNN(1, num_of_layers = num_of_layers)
if args.model == "BabyUnet":
	model = BabyUnet(1, num_of_layers = num_of_layers)
if args.model == "SingleConvolution":
	model = SingleConvolution(1, num_of_layers = num_of_layers)
if args.model == "Unet":
	model = Unet(1, num_of_layers = num_of_layers)


sum(p.numel() for p in model.parameters() if p.requires_grad)
image.ravel().shape

print("Done")
print("\n")


print("########## TRAINING ##########")

loss_function = MSELoss()
optimizer = Adam(model.parameters(), lr=0.01)
model = model.to(device)
noisy = noisy.to(device)

losses = []
val_losses = []
best_images = []
best_val_loss = 1

for i in range(iterations):
    model.train()
    
    net_input, mask = masker.mask(noisy, i % (masker.n_masks - 1))
    net_output = model(net_input)
    
    loss = loss_function(net_output*mask, noisy*mask)
    optimizer.zero_grad()
 
    loss.backward()
    
    optimizer.step()
    
    if i % 10 == 0:
        losses.append(loss.item())
        model.eval()
        
        net_input, mask = masker.mask(noisy, masker.n_masks - 1)
        net_output = model(net_input)
    
        val_loss = loss_function(net_output*mask, noisy*mask)
        
        val_losses.append(val_loss.item())
        
        print("(", i, ") Loss: \t", round(loss.item(), 5), "\tVal Loss: \t", round(val_loss.item(), 5))

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            denoised = np.clip(model(noisy).detach().cpu().numpy()[0, 0], 0, 1).astype(np.float64)
            best_psnr = peak_signal_noise_ratio(denoised, image)
            best_images.append(denoised)
            print("\tModel PSNR: ", np.round(best_psnr, 2))

denoised = best_images[-1]
peak_signal_noise_ratio(denoised, image)

imsave(output_image, denoised)

print("Done")
print("\n")