// Convert a microscopy image into the BioImageIT compatible format

/*
 * TODO
 *  - add all the OME-TIFF metadata to the json
 */

macro bioimageit_convert
{
	run("Close All");
	setBatchMode(true);
	arg = getArgument();
	// mode=file, file_path, destination_dir, data_name, author, date
    // mode=folder, source_dir, destination_dir, recursive, filter, author, date, directory_tag_key 

	//arg = "file,/Users/sprigent/Documents/data/mitosis-t1.tif,/Users/sprigent/BioImageIT/workspace/bioformat,mitosis,sprigent,2021-11-27";
	//arg = "folder,/Users/sprigent/Documents/data/spinning3_denoising/CELL01_crop,/Users/sprigent/BioImageIT/workspace/bioformat,true,endswith,.tif,sprigent,2021-11-27";
	print("arg = " + arg);
 	args = split(arg, ",");
 	if (args.length > 1)
 	{
 		if (args[0] == "file")
 		{
 			print("File mode");
 			if (args.length != 6){
 				print("ERROR: the file mode needs 6 input arguments");
 				return;
 			}
 			file_path = args[1];
 			destination_dir = args[2]; 
 			data_name = args[3]; 
 			author = args[4];
 			date = args[5];
 			import_image(file_path, destination_dir, data_name, author, date, "{}");
 			return;
 		}
 		else if (args[0] == "folder"){
 			print("Dir mode");
			if (args.length != 8){
 				print("ERROR: the folder mode needs 8 input arguments");
 				return;
 			}
 			source_dir = args[1];
 			destination_dir = args[2];
 			recursive = args[3];
 			filter = args[4];
 			author = args[5];
 			date = args[6];
 			directory_tag_key = args[7];
 			import_dir(source_dir, destination_dir, recursive, filter, author, date, directory_tag_key);
 			return;
 		}
 	}
 	else{
 		print("ERROR: The command line is not correct");
 		return;
 	}
	run("Close All");
	setBatchMode(false);
}

function import_dir(source_dir, destination_dir, recursive, filter, author, date, directory_tag_key)
{
	files = getFileList(source_dir);
	files = Array.sort(files);
	for (i = 0 ; i < files.length ; i++)
	{

		tags = "";
		if (directory_tag_key != "")
		{
			if (source_dir.endsWith(File.separator))
			{
				source_dir = source_dir.substring(0, source_dir.length -1)
			}
			dirs = split(source_dir, File.separator);
			value = dirs[dirs.length-1];
			tags = "{\""+directory_tag_key+"\": \""+value+"\"}";
		}

		// recursive on folder
		if (endsWith(files[i], File.separator) && recursive=="true" )
		{
			import_dir(source_dir + File.separator + files[i], destination_dir, recursive, filter, author, date, directory_tag_key);
		}
		// import image
		else if ( is_file_in_filter(files[i], filter))
		{
			original_file_path = source_dir + File.separator + files[i];
			point_idx = files[i].lastIndexOf(".");
			filename = files[i].substring(0,point_idx);	
			
			import_image(original_file_path, destination_dir, filename, author, date, tags);
		}
	}
}

function is_file_in_filter(filename, filter)
{
	res = matches(filename, filter);
	return res;
}

function import_image(original_file_path, destination_dir, data_name, author, date, tags)
{
	// open the image with BioFormat 
	// Do not use `open(…)` built-in function as it would try to open import pop-up in headless mode, and fail. 
	run("Bio-Formats Macro Extensions");
	Ext.openImagePlus(original_file_path);

	rename("input_image");
	metadata_json = get_metadata_to_json();

	getDimensions(width, height, channels, slices, frames);
	if (frames > 1)
	{
		save_movie_txt(channels, frames, destination_dir, data_name, author, date, tags, metadata_json);
	}
	else{
		if (channels > 1)
		{
			save_channels_data(channels, destination_dir, data_name, author, date, tags, metadata_json);
		}
		else{
			save_image(destination_dir, data_name, author, date, tags, metadata_json);
		}
	}
	run("Close All");
}

function get_metadata_to_json()
{
	getDimensions(width, height, channels, slices, frames);
	getVoxelSize(scale_x, scale_y, scale_z, unit);

	frame_interval = Stack.getFrameInterval();
	Stack.getUnits(X, Y, Z, time_unit, Value)

	metadata = "{\n";
	metadata += "    \"width\": "+width+",\n"; 
	metadata += "    \"height\": "+height+",\n"; 
	metadata += "    \"channels\": 1,\n"; 
	metadata += "    \"slices\": "+slices+",\n"; 
	metadata += "    \"frames\": "+frames+",\n"; 
	metadata += "    \"scale_x\": "+scale_x+",\n";
	metadata += "    \"scale_y\": "+scale_y+",\n"; 
	metadata += "    \"scale_z\": "+scale_z+",\n"; 
	metadata += "    \"unit\": \""+unit+"\",\n";
	metadata += "    \"frames interval\": "+frame_interval+",\n";
	metadata += "    \"time unit\": \""+time_unit+"\"\n";
	metadata += "}";  
	return metadata;
}

function get_date()
{
	getDateAndTime(year, month, dayOfWeek, dayOfMonth, hour, minute, second, msec);

	day_str = "";
	if (dayOfMonth<10) 
	{
		day_str = "0"+d2s(dayOfMonth, 0);
	}
	else
	{
		day_str = d2s(dayOfMonth, 0); 
	}
	return d2s(year, 0) + "-" + d2s(month, 0) + "-" + day_str;
}

function save_image(destination_dir, data_name, author, date, tags, metadata_json)
{
	saveAs("tiff", destination_dir + File.separator + data_name + ".tif");
	write_metadata(destination_dir, data_name, data_name + ".tif", author, "imagetiff", date, tags, metadata_json);
}

function add_zero_padding(idx, total)
{
	num_zeros = count_digits(total) - count_digits(idx);
	idx_str = "";
	for (i = 0 ; i < num_zeros ; i++)
	{
		idx_str += "0";	
	}
	idx_str += d2s(idx, 0);
	return idx_str;	
}

function count_digits(value)
{
	return floor(Math.log10(value)+1);
}

function save_movie_txt(channels, frames, destination_dir, data_name, author, date, tags, metadata_json)
{
	for (c = 1 ; c <= channels ; c++)
	{
		// Create the movie txt
		base_dest_name = data_name;
		if (channels > 1)
		{
			base_dest_name += "_c" + add_zero_padding(c, channels);
		}
		txt_filename = base_dest_name + ".txt";

		for (f = 1 ; f <= frames ; f++ )
		{
			// add frame to txt file
			frame_filename = base_dest_name + "_t" + add_zero_padding(f, frames) + ".tif";
			File.append(frame_filename, destination_dir + File.separator + txt_filename);

			// save frame as tif file
			run("Duplicate...", "duplicate channels="+c+" frames="+f);
			saveAs("tiff", destination_dir + File.separator + frame_filename);
			close();
		}
		write_metadata(destination_dir, base_dest_name, txt_filename, author, "movietxt", date, tags, metadata_json);
	}
	print("save_movie_txt done");
}

function save_channels_data(channels, destination_dir, data_name, author, date, tags, metadata_json)
{
	for (c = 1 ; c <= channels ; c++)
	{
		base_dest_name = data_name;
		base_dest_name += "_c" + add_zero_padding(c, channels);
		run("Duplicate...", "duplicate channels="+c);
		saveAs("tiff", destination_dir + File.separator + base_dest_name + ".tif");
		write_metadata(destination_dir, base_dest_name, base_dest_name + ".tif", author, "imagetiff", date, tags, metadata_json);
		close();
	}
}

function write_metadata(destination_dir, data_name, data_filename, author, format, date, tags, metadata_json)
{
	md_json_file = destination_dir + File.separator + data_name + ".md.json";
	content = "";
	content + = "{\n";
    content + = "\"origin\": {\n";
    content + = "    \"type\": \"raw\"\n";
    content + = "},\n";
    content + = "\"common\": {\n";
    content + = "    \"name\": \""+data_name+"\",\n";
    content + = "    \"author\": \""+author+"\",\n";
    content + = "    \"date\": \""+date+"\",\n";
    content + = "    \"format\": \""+format+"\",\n";
    content + = "    \"url\": \""+data_filename+"\"\n";
    content + = "},\n";
    content + = "\"tags\": "+tags+",\n";
    content += "\"metadata\": "+metadata_json+"\n";
    content + = "}\n";
    File.append(content, md_json_file);
    File.append(data_name + ".md.json", destination_dir + File.separator + "tmp.txt");
}
