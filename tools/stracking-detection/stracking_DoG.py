import os
import numpy as np
import argparse
from skimage.io import imread
from stracking.detectors import DoGDetector
from stracking.io import write_particles


def read_txt_movie_list(path):
    # Opening file
    file1 = open(path, 'r')
    frames = []
    for line in file1:
        frames.append(line.strip())
    file1.close()   
    return frames 


def read_movie_txt(path):
    parent_dir = os.path.dirname(path)
    frames = read_txt_movie_list(path)
    X_data = []
    for frame in frames:
        X_data.append(imread(os.path.join(parent_dir, frame)))
    return np.array(X_data)


def main():
    """Create the parameters"""
    
    parser = argparse.ArgumentParser(description = 'stracking DoG dectection')
    
    parser.add_argument('-i', '--input', help = 'Input image')
    parser.add_argument('-o', '--output', help = 'Output file')
    parser.add_argument('-mi', '--min_sigma_value', help = 'Minimal sigma value', default = '1')
    parser.add_argument('-max', '--max_sigma_value', help = 'Minimal sigma value', default = '5')
    parser.add_argument('-r', '--ratio', help = 'Sigma ratio', default = '1.6')
    parser.add_argument('-t', '--threshold', help = 'Threshold', default = '0.2')
    parser.add_argument('-ov', '--overlap', help = 'Overlap', default = '0.5')
    
    args = parser.parse_args()
    
    input_ = args.input
    output = args.output
    min_sigma = float(args.min_sigma_value)
    max_sigma = float(args.max_sigma_value)
    threshold = float(args.threshold)
    ratio = float(args.ratio)
    overlap = float(args.overlap)
    
    detector = DoGDetector(min_sigma = min_sigma, max_sigma = max_sigma, sigma_ratio = ratio, threshold = threshold, overlap = overlap)
    out = detector.run(read_movie_txt(input_))
    write_particles(output, out)
    

if __name__ == "__main__":
    main()