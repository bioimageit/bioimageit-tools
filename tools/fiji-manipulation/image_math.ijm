macro invert{

	// parse args
	args = parseArgs();

	// open the data
	open(args[0]);
	image = getTitle();

	operator = args[1]
	value = args[2]

	// run
	run(operator + "...", "value="+value);

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
