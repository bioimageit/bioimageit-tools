macro invert{

	// parse args
	args = parseArgs();

	// open the data
	open(args[0]);
	image1 = getTitle();

	open(args[1]);
	image2 = getTitle();

	// run
	operation = args[2]
	imageCalculator(operation + " create 32-bit", image1, image2);

	// save result image
	saveAs("TIFF", args[3]);

}

function parseArgs(){
	argsStr = getArgument()
	argsStr = substring(argsStr, 1, lengthOf(argsStr)); // remove first char
	argsStr = substring(argsStr, 0, lengthOf(argsStr)-1); // remove last char
	print(argsStr);
	args = split(argsStr, ",");
	for (i=0 ; i < args.length ; i++){
		print(args[i]);
	}
	return args;
}
