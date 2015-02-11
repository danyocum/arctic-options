import arcpy
import os
import pickle
import time
import gc

DEBUG=True
#Alaska Albers Equal Area Conic
ALASKA_SR = 102006
#polar projection
POLAR_SR = 7215
ALASKA_EXT= "_alaska"
POLAR_EXT = "_polar"
class Toolbox(object):

    def __init__(self):
       self.label = "EraseShorelineToolbox"
       self.alias = "EraseShorelineToolbox"

       # List of tool classes associated with this toolbox
       self.tools = [FindLayersToEraseShoreline]

class FindLayersToEraseShoreline(object):

    def __init__(self):
        """Define the tool (PolarToolbox name is the name of the class)."""
        self.label = "FindLayersToEraseShoreline"
        self.description = "erase shoreline "
        self.canRunInBackground = False

    def getParameterInfo(self):
        params = []
        return params

    def updateParameters(self, parameters):
        return

       

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True


    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def print_time(self, debug, msg, start_time):
        if debug:
            arcpy.AddMessage("{0} took {1} seconds".format(msg, time.time()-start_time))
        return time.time()

    def execute(self, parameters, messages):
        working_dir = r"c:\arctic_options_shipping"
        shoreline_line_file = r"c:\arctic_options_shipping\simple_shoreline.gdb\arctic_shoreline_simplified_dissolved"
        #shoreline_line_file = r"c:\arctic_options_shipping\simplified_arctic_shoreline\arctic_shoreline_simplified_line.shp"
        #shoreline_file = r"c:\arctic_options_shipping\shoreline.gdb\arctic_shoreline_simpler_2k"
        #track_file = r"c:\arctic_options_shipping\shipping_tracks.gdb\ais_tracks_subset"
        track_file = r"c:\arctic_options_shipping\shipping_tracks.gdb\ais_tracks_with_shoreline_split"

        #output_track_file = r"c:\arctic_options_shipping\shipping_tracks.gdb\ais_tracks_noland_skipped"
        #need_to_be_erased_file = r"c:\arctic_options_shipping\shipping_tracks.gdb\ais_tracks_noland_skipped"
        #empty_tracks_file = r"c:\arctic_options_shipping\shipping_tracks.gdb\ais_tracks_empty"
        keep_tracks_pickle = r"keep_tracks_pickle"
        erase_tracks_pickle = r"erase_tracks_pickle"
        arcpy.env.overwriteOutput = True
        #shoreline_file = os.path.join(working_dir, shoreline_filename)
        arcpy.AddMessage("copying shoreline into memory")
        #inmem_shoreline = arcpy.CopyFeatures_management(shoreline_file, r"in_memory\shoreline_inmem")
        inmem_shoreline_line = arcpy.CopyFeatures_management(shoreline_line_file, r"in_memory\shoreline_inmem_line")
        #inmem_newtracks = arcpy.CopyFeatures_management(empty_tracks_file, r"in_memory\empty_tracks")
        #inmem_shoreline = shoreline_file
        #inmem_shoreline_line = shoreline_line_file
        #inmem_newtracks = empty_tracks
        #shoreline_file = os.path.join(working_dir, shoreline_filename)
        #track_file = os.path.join(working_dir, track_filename)

        #this is the starting row if the script crashes/hangs - which it seems to every few thousand iterations
        startrow = 0
        total_rows = int(arcpy.GetCount_management(track_file).getOutput(0))
        arcpy.AddMessage("num total tracks is {}".format(total_rows))
        #save_trigger = 1000
        #if it crashes and we need to restart, make sure this gets set at the right #

        keep_list = []
        erase_list = []
        startrow = 0

        track_lyr = r"in_memory\inmem_track"
        arcpy.MakeFeatureLayer_management(track_file, track_lyr)

        arcpy.AddMessage("startrow: {}; totrows:{}".format(startrow, total_rows))
        for total_count in range(startrow, total_rows):
            if total_count %100 == 0:
                arcpy.AddMessage("processing track {} of {}".format(startrow, total_rows))
            #curr_layer = None 

            where_clause = "OBJECTID = {}".format(total_count)
            #curr_layer = r"in_memory\tracklayer"
            #arcpy.MakeFeatureLayer_management(track_file, curr_layer, where_clause)

            arcpy.SelectLayerByAttribute_management(track_lyr, "NEW_SELECTION", where_clause)
            #self.print_time(DEBUG, "by attribute", start_time)

            track_selection_count = int(arcpy.GetCount_management(track_lyr).getOutput(0) or 0)

            if track_selection_count > 0: 
                arcpy.SelectLayerByLocation_management(track_lyr, "INTERSECT", inmem_shoreline_line, "", "SUBSET_SELECTION")
                #self.print_time(DEBUG, "location", start_time)

                selcount = int(arcpy.GetCount_management(track_lyr).getOutput(0) or 0)
                arcpy.SelectLayerByAttribute_management(track_lyr, "CLEAR_SELECTION")
                
                if selcount > 0:
                    erase_list.append(total_count)
                else:
                    keep_list.append(total_count)

        keep_file = os.path.join(working_dir, keep_tracks_pickle+".txt")
        erase_file = os.path.join(working_dir, erase_tracks_pickle+".txt")
        arcpy.AddMessage("keeping {} tracks".format(len(keep_list)))
        pickle.dump(keep_list, open( keep_file, "wb" ))
        arcpy.AddMessage("erasing {} tracks".format(len(erase_list)))
        pickle.dump(erase_list, open(erase_file, "wb"))


