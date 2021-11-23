//#@file (label="Txt movie file") in_file

macro read_txtmovie{

	
	txt_file_path = "";
	if (lengthOf(getArgument()) == 0){
		txt_file_path = in_file;
		return;
	}
	else{
		txt_file_path = getArgument();	
		
	}
	print("txt_file_path = " + txt_file_path);

	if (!File.exists(txt_file_path))
	{
		print("ERROR: The file " + txt_file_path + " does not exists");
		return;
	}

	setBatchMode(true);

	filename = File.getName(txt_file_path);
	frames = parse_txt_file(txt_file_path);

	// load the first frame
	open(frames[0]);
	rename(filename);
	// load and concatenate the other frames
	for (i=1 ; i < frames.length ; i++)
	{
		open(frames[i]);
		next_frame = getTitle();
		run("Concatenate...", "  title="+filename+" open image1="+filename+" image2="+next_frame+"");
	}
	setBatchMode(false);
}

function parse_txt_file(txt_file_path)
{

		file_content = File.openAsString(txt_file_path);
		lines = split(file_content, "\n");
		parent_dir = File.getParent(txt_file_path);
		for (i=0 ; i < lines.length ; i++)
		{
			lines[i] = parent_dir + File.separator + lines[i];
		}
		return lines;

	
}
