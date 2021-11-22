macro invert{

	// parse args
	args = parseArgs();

	// open the data
	print(args[0])
	open(args[0]);

	// Invert
	run("Invert");

	// save result image
	saveAs("TIFF", args[1]);

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
