import os
import sys
import getopt

from n2v.models import N2VConfig, N2V
from n2v.internals.N2V_DataGenerator import N2V_DataGenerator
from csbdeep.io import save_tiff_imagej_compatible
from tifffile import imread


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
                       train_steps_per_epoch=steps_per_epoch,
                       train_epochs=epochs, train_loss='mse', batch_norm=True,
                       train_batch_size=batch_size, n2v_perc_pix=0.198,
                       n2v_patch_shape=(int(patch_size_z), int(patch_size_xy), int(patch_size_xy)),
                       n2v_manipulator='uniform_withCP',
                       n2v_neighborhood_radius=neighborhood_radius)
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


def main(argv):
    inputfile = ''
    outputfile = ''
    patch_size_xy = 64
    patch_size_z = 32
    epochs = 20
    steps_per_epoch = 200
    batch_size = 4
    neighborhood_radius = 5

    try:
        opts, args = getopt.getopt(argv,"hi:o:x:z:e:s:b:n:",["ifile=","ofile=","patchxy=","patchz=","epochs=","steps=", "batch", "neigh="])
    except getopt.GetoptError:
        print('noise2void_train_predict.py -i <inputfile> -o <outputfile> ...')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('noise2void_train_predict.py -i <inputfile> -o <outputfile> ...')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
        elif opt in ("-x", "--patchxy"):
            patch_size_xy = int(arg)
        elif opt in ("-z", "--patchz"):
            patch_size_z = int(arg)
        elif opt in ("-e", "--epochs"):
            epochs = int(arg)
        elif opt in ("-s", "--steps"):
            steps_per_epoch = int(arg)
        elif opt in ("-b", "--batch"):
            batch_size = int(arg)
        elif opt in ("n", "--neigh"):
            neighborhood_radius = int(arg)

    # print params
    print('inputfile:', inputfile)
    print('outputfile:', outputfile)
    print('patch_size_xy:', patch_size_xy)
    print('patch_size_z:', patch_size_z)
    print('epochs:', epochs)
    print('steps_per_epoch:', steps_per_epoch)
    print('batch_size:', batch_size)
    print('neighborhood_radius:', neighborhood_radius)

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


if __name__ == "__main__":
    main(sys.argv[1:])
