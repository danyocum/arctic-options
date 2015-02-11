import arcpy
import glob
import pickle
import numpy

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
        self.tools = [EraseShoreline]

class EraseShoreline(object):
    
    def __init__(self):
        """Define the tool (PolarToolbox name is the name of the class)."""
        self.label = "EraseShoreline"
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

    def execute(self, parameters, messages):
        working_dir = r"c:\arctic_options_shipping"
        keep_glob = "keep_tracks_pickle.txt"
        #erase_glob = "erase_tracks_pickle_*.txt"

        keep_files = glob.glob(keep_glob)
        #erase_files = glob.glob(erase_glob)

        keep_list = []
        for kf in keep_files:
            kl = pickle.load(open(kf, "rb"))
            keep_list.extend(kl)

        """
        erase_list = []
        for ef in erase_files:
            el = pickle.load(open(ef, "rb"))
            erase_list.extend(el)
        """
        also_keep_pickle = "really_keep_tracks_pickle.txt"
        really_erase_pickle = "really_erase_tracks_pickle.txt"

        also_keep_list = pickle.load(open(also_keep_pickle, "rb"))
        really_erase_list = pickle.load(open(really_erase_pickle, "rb"))

        arcpy.env.workspace = working_dir
        arcpy.env.overwriteOutput = True
        arcpy.AddMessage("number to erase {}".format(len(really_erase_list)))

        arcpy.AddMessage("number of original list to keep {}".format(len(keep_list)))
        arcpy.AddMessage("number of new list to keep {}".format(len(also_keep_list)))

        arcpy.AddMessage("copying original file to no land file")
        orig_track_file = r"c:\arctic_options_shipping\shipping_tracks.gdb\ais_tracks_with_shoreline_split"
        keep_track_file = r"c:\arctic_options_shipping\shipping_tracks.gdb\ais_tracks_no_land_overlap"
        arcpy.CopyFeatures_management(orig_track_file, keep_track_file)

        arcpy.AddMessage("now updating...")
        with arcpy.da.UpdateCursor(keep_track_file, ["OBJECTID"]) as cursor:
            for row in cursor:
                oid = row[0]
                if not (oid in keep_list) and not (oid in also_keep_list):
                    cursor.deleteRow()

        arcpy.AddMessage("copying original file to erase file")
        orig_track_file = r"c:\arctic_options_shipping\shipping_tracks.gdb\ais_tracks_with_shoreline_split"
        erase_track_file = r"c:\arctic_options_shipping\shipping_tracks.gdb\ais_tracks_with_land_overlap"
        arcpy.CopyFeatures_management(orig_track_file, erase_track_file)
        with arcpy.da.UpdateCursor(erase_track_file, ["OBJECTID"]) as cursor:
            for row in cursor:
                oid = row[0]
                if not (oid in really_erase_list):
                    cursor.deleteRow()
        
        return
