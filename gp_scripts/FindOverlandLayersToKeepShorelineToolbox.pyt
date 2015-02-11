import arcpy
import os
import pickle
import time
import glob

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

    def get_erase_object_ids(self):
        
        #keep_glob = "keep_tracks_pickle_*.txt"
        erase_glob = "erase_tracks_pickle.txt"

        erase_files = glob.glob(erase_glob)
        arcpy.AddMessage('erase files: {}'.format(erase_files))
        erase_list = []
        for ef in erase_files:
            el = pickle.load(open(ef, "rb"))
            erase_list.extend(el)

        arcpy.AddMessage("erasing:")
        arcpy.AddMessage("{}".format(len(erase_list)))
        return erase_list

    def execute(self, parameters, messages):
        arcpy.AddMessage("Finding which overlapping tracks are completely within land, keeping those...")
        arcpy.env.overwriteOutput = True
        working_dir = r"c:\arctic_options_shipping"
        arcpy.env.workspace = working_dir
        shoreline_line_file = r"c:\arctic_options_shipping\simple_shoreline.gdb\arctic_shoreline_simplified_dissolved"

        track_file = r"c:\arctic_options_shipping\shipping_tracks.gdb\ais_tracks_with_shoreline_split"


        erase_tracks_pickle = r"really_erase_tracks_pickle"
        keep_tracks_pickle = r"really_keep_tracks_pickle"
        

        inmem_shoreline_line = arcpy.CopyFeatures_management(shoreline_line_file, r"in_memory\shoreline_inmem_line")

        objid_list = self.get_erase_object_ids()

        total_rows = len(objid_list)

        arcpy.AddMessage("num total tracks is {}".format(total_rows))
       
        keep_list = []
        erase_list = []

        track_lyr = r"in_memory\inmem_track"
        arcpy.MakeFeatureLayer_management(track_file, track_lyr)
        i=0
        for objid in objid_list:
            i+=1
            arcpy.AddMessage("working on {} of {}".format(i, total_rows))

            where_clause = "OBJECTID = {}".format(objid)

            arcpy.SelectLayerByAttribute_management(track_lyr, "NEW_SELECTION", where_clause)
            #self.print_time(DEBUG, "by attribute", start_time)

            track_selection_count = int(arcpy.GetCount_management(track_lyr).getOutput(0) or 0)
            if track_selection_count > 0: 

                arcpy.SelectLayerByLocation_management(track_lyr, "COMPLETELY_WITHIN", inmem_shoreline_line, "", "SUBSET_SELECTION")
                #self.print_time(DEBUG, "location", start_time)

                selcount = int(arcpy.GetCount_management(track_lyr).getOutput(0) or 0)
                
                if selcount > 0:
                    keep_list.append(objid)
                else:
                    erase_list.append(objid)
            else:
                arcpy.AddMessage("THIS SHOULDNT HAPPEN: no track for objid {}".format(objid))

            arcpy.SelectLayerByAttribute_management(track_lyr, "CLEAR_SELECTION")

        keep_file = os.path.join(working_dir, keep_tracks_pickle+".txt")
        erase_file = os.path.join(working_dir, erase_tracks_pickle+".txt")

        arcpy.AddMessage("keeping {} tracks".format(len(keep_list)))
        pickle.dump(keep_list, open( keep_file, "wb" ))
        arcpy.AddMessage("erasing {} tracks".format(len(erase_list)))
        pickle.dump(erase_list, open(erase_file, "wb"))


