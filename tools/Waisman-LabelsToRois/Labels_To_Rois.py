#!/usr/bin/python

print("########## IMPORTS ##########")

from javax.swing import JFrame, JPanel, JLabel, JButton, JTextField, JFileChooser, JMenuBar, JMenu, JMenuItem, JProgressBar, BoxLayout, Box
from javax.swing import JOptionPane
from javax.swing import JRadioButton,ButtonGroup
from javax.swing import BoxLayout, Box
from java.awt import FlowLayout
from ij import IJ
from ij.plugin.frame import RoiManager
from ij.plugin import RoiEnlarger
from ij.process import ImageProcessor
from ij.measure import ResultsTable, Measurements
from ij.plugin.filter import ParticleAnalyzer
from datetime import time, tzinfo
# from ij.gui import Wand
from javax.swing import SwingWorker, SwingUtilities
# from java.util.concurrent import ExecutionException
# from java.awt import Toolkit as awtToolkit
from tempfile import NamedTemporaryFile
from ij.macro import Variable
from os import listdir
from os.path import isfile, join
import time
import datetime
import math
import os
import re
import argparse
import csv

print("Done")
print("\n")

###########################################################
####################  Before we begin #####################
###########################################################

print("########## BEFORE WE BEGIN ##########")

parser = argparse.ArgumentParser()
parser.add_argument('--original', type = argparse.FileType('r'), help = 'original image')
parser.add_argument('--label', type = argparse.FileType('r'), help = 'label image, from cellpose for instance')
parser.add_argument('--csv', type = argparse.FileType('r'))
args = parser.parse_args()

print("original & label in the command line")

gvars = {} # Create dictionary to store variables created within functions
gvars['eroded_pixels'] = 0 # initialize

myTempFile = NamedTemporaryFile(suffix='.zip')
gvars['tempFile'] = myTempFile.name

# Setting orginal & label images
original = args.original.name
label_name = args.label.name
print("Original : {}".format(original))
print("Label : {}".format(label_name))


original_dirname = os.path.dirname(original)
label_dirname = os.path.dirname(label_name)
print("Original image dirname : {}".format(original_dirname))
print("Label image dirname : {}".format(label_dirname))

# Set the original directory of the filechooser to the home folder
gvars['original_JFileChooser'] = original_dirname
gvars['path_JFileChooser'] = gvars['original_JFileChooser']

print("Original & label selected")

print("\n")

###########################################################
#################  Define LabelToRoi_Task #################
###########################################################

print("########## DEFINITION OF SwingWorker ##########")

class LabelToRoi_Task(SwingWorker):

    def __init__(self, imp):
        SwingWorker.__init__(self)
        self.imp = imp

    def doInBackground(self):
        imp = self.imp

        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        print("Started at : {}".format(st))

        # # Disable frame3 buttons in GUI while loading ROIs
        # f2_btn_original.setEnabled( 0 )
        # f2_btn_label.setEnabled( 0 )
        # f2_btn_prev.setEnabled( 0 )
        # f2_btn_next.setEnabled( 0 )


        RM = RoiManager()        # we create an instance of the RoiManager class
        rm = RM.getRoiManager()  # "activate" the RoiManager otherwise it can behave strangely
        rm.reset()
        rm.runCommand(imp,"Show All without labels") # we make sure we see the ROIs as they are loading


        imp2 = imp.duplicate()
        ip = imp2.getProcessor()
        width = imp2.getWidth()
        height = imp2.getHeight() - 1

        max_label = int(imp2.getStatistics().max)
        max_digits = int(math.ceil(math.log(max_label,10))) # Calculate the number of digits for the name of the ROI (padding with zeros)
        IJ.setForegroundColor(0, 0, 0) # We pick black color to delete the label already computed

        for j in range(height):
           for i in range(width):
              current_pixel_value = ip.getValue(i,j)
              if current_pixel_value > 0:
                 IJ.doWand(imp2, i, j, 0.0, "Legacy smooth");

                 # We add this ROI to the ROI manager
                 roi = imp2.getRoi()
                 roi.setName(str(int(current_pixel_value)).zfill(max_digits))
                 rm.addRoi(roi)

                 ip.setColor(0); # Fix 32 bit issue
                 ip.fill(roi) # Much faster than IJ.run(imp2, "Fill", ....

                 # Update ProgressBar
                 progress = int((current_pixel_value / max_label) * 100)
                 self.super__setProgress(progress)

        rm.runCommand(imp,"Sort") # Sort the ROIs in the ROI manager
        rm.runCommand(imp,"Show All without labels")

        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

        print("Finished at : {}".format(st))


    # def done(self):
    #     try:
    #         self.get()  #raise exception if abnormal completion
    #         # awtToolkit.getDefaultToolkit().beep()

    #         RM = RoiManager()
    #         rm = RM.getRoiManager()
    #         self.super__setProgress(100) #
    #         rm.runCommand(self.imp,"Show All without labels")

    #         ### We save a temporary RoiSet
    #         temp_roi_path = gvars['tempFile']
    #         rm.runCommand("Save", temp_roi_path)
    #         print "Temp ROIs Saved"

            # # We change visibility from frame2 to frame3 once the labelToRoi finishes loading rois
            # frame3.setVisible(True)
            # frame2.setVisible(False)

            # # Enable frame3 buttons in GUI after loading
            # f2_btn_original.setEnabled( 1 )
            # f2_btn_label.setEnabled( 1 )
            # f2_btn_prev.setEnabled( 1 )
            # f2_btn_next.setEnabled( 1 )

        # except ExecutionException, e:
        #     raise SystemExit, e.getCause()


print("Done")
print("\n")

###########################################################
###################  Def save csv #########################
###########################################################

print("########## DEFINITION OF saveTable FUNCTION ##########")
row = 0

def saveTable():
    print "Saving Table..."
    RM = RoiManager()        # we create an instance of the RoiManager class
    rm = RM.getRoiManager()
    instance = RoiManager.getInstance()
    imp = gvars["workingImage"]
    table_message = []
    
    is_scaled = imp.getCalibration().scaled()
    if not is_scaled:
        print("Warning: your image is not spatially calibrated. To calibrate, go to Analyze > Set Scale... \n")

    nChannels = imp.getNChannels()
    print("Total channels: {}".format(nChannels))
    
    for current_channel in range(1,nChannels+1):
        print("Current channel: {}".format(current_channel))

    imp.setSlice(current_channel)
    current_slice = str(imp.getCurrentSlice()) #Get current slice for saving into filename
    print("Current slice: {}".format(current_slice))

    is_scaled = imp.getCalibration().scaled()
    if is_scaled:
        spatial_cal = "True"
    else:
        spatial_cal = "False"

    IJ.run("Clear Results", "")
    rm.runCommand(imp,"Select All");
    rm.runCommand(imp,"Measure")

    table = ResultsTable.getResultsTable().clone()
    # table.show("Tabla actualizada")
    IJ.selectWindow("Results")
    IJ.run("Close")

    filename = os.path.split(gvars["path_original_image"])[1]
    # print("Filename : {}".format(filename))

    pixels = gvars['eroded_pixels'] # To save number of eroded pixels in table and table name
    print("eroded_pixels in gvars")
    
    # test
    row = 0
    for roi in instance.getRoisAsArray():
        row = row + 1
        # print("row = {}".format(row))


    print("Table size : {}".format(row))
    for i in range(0, row):
        table.setValue('File', i, str(filename))
        table.setValue('Channel', i, current_channel)
        table.setValue('Pixels_eroded', i, str(pixels))
        table.setValue('Spatial_calibration', i, spatial_cal)
    print("File, Channel, Pixels_eroded, Spatial_calibration set : {}".format(row))

    table.show("Tabla actualizada")


    path_to_table = str(gvars['path_original_image'].replace(".tif", "") + "_Erosion_" +str(pixels)+ "px_Channel_" + str(current_channel) + ".csv")
    print("CSV table will be saved as : {}".format(path_to_table))

    IJ.saveAs("Results", path_to_table)
    IJ.run("Close")


    table_message.append("Table saved to %s" % path_to_table)
    print("CSV table saved")

    path_to_multichannel_table = str(gvars['path_original_image'].replace(".tif", "") + "_Erosion_" +str(pixels)+ "px_AllChannels" + ".csv")


    # try:
    #     if current_channel ==1:
    #         multichannel_table_file = open(path_to_multichannel_table, 'w')
    #         current_table =  open(path_to_table, 'r')
    #         first_line = next(current_table)
    #         multichannel_table_file.writelines(first_line)
    #         multichannel_table_file.close()
    #         current_table.close()

    #         with open(path_to_multichannel_table, 'a') as multichannel_table_file, open(path_to_table, 'r') as current_table:
    #             _ = next(current_table) # To avoid appending the header again and again in every iteration
    #             for line in current_table:
    #                 multichannel_table_file.writelines(line)

    # except IOError as e:
    #     print("Error: The file {} is open.\nPlease close it and try again!".format(path_to_multichannel_table))
    #     print e
    #     return #Stop running


print("Done")
print("\n")


###########################################################
#################  Images to gvars ########################
###########################################################

print("########## IMAGE TO GVARS ##########")

print('Open original image...')
gvars['path_original_image'] = str(original)
gvars['path_JFileChooser'] = original_dirname
print("path_original_image in gvars \n")


print('Open label image...')
gvars['path_label_image'] = str(label_name)
gvars['path_JFileChooser'] = label_dirname
print("path_label_image in gvars")


# print("test LabelToRoi_Task")
# LabelToRoi_Task(original)
# print("LabelToRoi_Task done")

print("\n")

###########################################################
#####################  Some Work ##########################
###########################################################

print("########## SOME WORK ##########")

if 'path_label_image' not in gvars:
    print("You have to choose at least a label image \n")

elif 'path_original_image' in gvars:
    print("path_original_image in gvars \n")
    imp = IJ.openImage(gvars['path_original_image']) # IF there isn't an original image, we'll work only and display the results on the label image

else:
    gvars['path_original_image'] = gvars['path_label_image']
    imp = IJ.openImage(gvars['path_label_image']) # If there is not an original image and only working with the lable, then show the results of the label

if 'path_original_image' in gvars and 'path_label_image' in gvars:
    print("path_original_image in gvars and path_label_image in gvars")
    RM = RoiManager()        # we create an instance of the RoiManager class
    rm = RM.getRoiManager()

    gvars["workingImage"] = imp
    IJ.run(imp, "Enhance Contrast", "saturated=0.35");

    imp2 = IJ.openImage(gvars['path_label_image'])
    task = LabelToRoi_Task(imp2) # Executes the LabelToRoi function defined on top of this script. It is wrapped into a SwingWorker in order for the windows not to freeze
    # task.addPropertyChangeListener(update_progress) # To update the progress bar
    print("LabelToRoi_Task on {}".format(imp2))
    task.execute()
    print("LabelToRoi_Task done on {}".format(imp2))

    print("\n")

#     rm.runCommand(imp,"Show All without labels")

    # f3_txt1.setText("0")



# Save csv table
saveTable()


print("\n")
print("Congrats, you made it folks !")