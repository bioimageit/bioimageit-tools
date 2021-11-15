import os
import os.path
import sys, getopt

import pycudadecon
from skimage import io

def main(argv):
    inputfile = ''
    outputfile = ''
    dxdata = 0.1
    dzdata = 0.5
    angle = 31.5
    width = 0
    shift = 0
    pad_val="auto"
    try:
        opts, args = getopt.getopt(argv,"i:o:x:z:a:w:s:p:",["ifile=","ofile=","dxdata=","dzdata=","angle=","width=","shift=", "pad="])
    except getopt.GetoptError:
        print('cudadeskew.py -i <ifile> -o <ofile> -x <dxdata> -z <dzdata> -a <angle> -w <width> -s <shift> -p <pad>')
        sys.exit(2)
    for opt, arg in opts:
        # print('opt=', opt)
        # print('arg=', arg)
        if opt == '-h':
            print('cudadeskew.py -i <ifile> -o <ofile> -x <dxdata> -z <dzdata> -a <angle> -w <width> -s <shift> -p <pad>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
        elif opt in ("-x", "--dxdata"):
            dxdata = float(arg)   
        elif opt in ("-z", "--dzdata"):
            dzdata = float(arg)   
        elif opt in ("-a", "--angle"):
            angle = float(arg)  
        elif opt in ("-w", "--width"):
            width = float(arg)  
        elif opt in ("-s", "--shift"):
            shift = float(arg) 
        elif opt in ("-p", "--pad"):
            pad_val = arg              

    # print params
    print('inputfile:', inputfile)
    print('outputfile:', outputfile)  
    print('dxdata:', dxdata)  
    print('dzdata:', dzdata)     
    print('angle:', angle)   
    print('width:', width)   
    print('shift:', shift)    
    print('pad_val:', pad_val)                  

    # run
    im = io.imread(inputfile)
    out_im = pycudadecon.deskewGPU(im, dxdata=dxdata, dzdata=dzdata, angle=angle, width=width, shift=shift, pad_val=pad_val)
    io.imsave(outputfile, out_im)

    print('Input file is "', inputfile)
    print('Output file is "', outputfile)


if __name__ == "__main__":
   main(sys.argv[1:])
