import os
import numpy as np
import argparse
from skimage.io import imread
from stracking.detectors import DoHDetector
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
    
    parser = argparse.ArgumentParser(description = 'stracking DoH dectection')
    
    parser.add_argument('-i', '--input', help = 'Input image')
    parser.add_argument('-o', '--output', help = 'Output file')
    parser.add_argument('-mi', '--min_sigma_value', help = 'Minimal sigma value', default = '1')
    parser.add_argument('-max', '--max_sigma_value', help = 'Minimal sigma value', default = '5')
    parser.add_argument('-n', '--num_sigma', help = 'Number sigmas', default = '10')
    parser.add_argument('-t', '--threshold', help = 'Threshold', default = '0.2')
    parser.add_argument('-ov', '--overlap', help = 'Overlap', default = '0.5')
    parser.add_argument('-l', '--log_scale', help = 'Log scale', default = 'False')
    
    args = parser.parse_args()
    
    input_ = args.input
    output = args.output
    min_sigma = float(args.min_sigma_value)
    max_sigma = float(args.max_sigma_value)
    threshold = float(args.threshold)
    overlap = float(args.overlap)
    num_sigma = int(args.num_sigma)
    log_scale = args.log_scale
    
    detector = DoHDetector(min_sigma = min_sigma, max_sigma = max_sigma, num_sigma = num_sigma, threshold = threshold, overlap = overlap, log_scale = log_scale)
    out = detector.run(read_movie_txt(input_))
    write_particles(output, out)


if __name__ == "__main__":
    main()
