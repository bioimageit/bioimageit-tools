import os
import os.path
import sys, getopt

import pycudadecon
from skimage import io

def main(argv):
    inputfile = ''
    outputfile = ''
    psf = ''    
    background = 80
    try:
        opts, args = getopt.getopt(argv,"i:o:p:b:",["ifile=","ofile=","psf=", "background="])
    except getopt.GetoptError:
        print('cudadecon.py -i <ifile> -o <ofile> -p <psf> -b <background>')
        sys.exit(2)
    for opt, arg in opts:
        # print('opt=', opt)
        # print('arg=', arg)
        if opt == '-h':
            print('cudadecon.py -i <ifile> -o <ofile> -p <psf> -b <background>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
        elif opt in ("-p", "--psf"):
            psf = arg      
        elif opt in ("-b", "--background"):
            background = float(arg)                

    # print params
    print('inputfile:', inputfile)
    print('outputfile:', outputfile) 
    print('psf:', psf)  
    print('background:', background)                   

    # run
    im = io.imread(inputfile)
    out_im = pycudadecon.decon(im, psf, background=background)
    io.imsave(outputfile, out_im)

    print('Input file is "', inputfile)
    print('Output file is "', outputfile)


if __name__ == "__main__":
   main(sys.argv[1:])
