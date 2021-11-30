import stracking
import argparse
import os
import pandas
from skimage.io import imread
from stracking.detectors import LoGDetector


def main():
	"""Create the parameters"""

	parser = argparse.ArgumentParser(description = 'stracking LoG dectection')

	parser.add_argument('-i', '--input', help = 'Input image')
	parser.add_argument('-o', '--output', help = 'Output file')
	parser.add_argument('-mi', '--min_sigma_value', help = 'Minimal sigma value', default = '1')
	parser.add_argument('-max', '--max_sigma_value', help = 'Minimal sigma value', default = '5')
	parser.add_argument('-t', '--threshold', help = 'Threshold', default = '0.2')
	parser.add_argument('-r', '--ratio', help = 'Sigma ratio', default = '1.6')
	parser.add_argument('-ov', '--overlap', help = 'Overlap', default = '0.5')
	parser.add_argument('-n', '--num_sigma', help = 'Number sigmas', default = '10')
	parser.add_argument('-l', '--log_scale', help = 'Log scale', default = 'False')

	args = parser.parse_args()

	input_ = args.input
	output = args.output
	min_sigma = float(args.min_sigma_value)
	max_sigma = float(args.max_sigma_value)
	threshold = float(args.threshold)
	ratio = float(args.ratio)
	overlap = float(args.overlap)
	num_sigma = int(args.num_sigma)
	log_scale = args.log_scale

	detector = LoGDetector(min_sigma = min_sigma, max_sigma = max_sigma, 
		                   num_sigma = num_sigma, threshold = threshold,
						   overlap = overlap, log_scale = log_scale)
	out = detector.run(imread(input_))
	print(type(out))

	SParticules.data


if __name__ == "__main__":
    main()