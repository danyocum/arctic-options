import arcpy
import os
import pickle
import gc
import numpy

DEBUG=True
#Alaska Albers Equal Area Conic
ALASKA_SR = 102006
#polar projection
POLAR_SR = 7215
ALASKA_EXT= "_alaska"
POLAR_EXT = "_polar"
M_TO_MILES = 6.2137e-4
MMSI_COL = "MMSI"
DATE_COL = "DATE"
NAV_COL = "NAV"
ROT_COL = "ROT"
TIME_COL = "TIME"
TRUEHEAD_COL = "TRUEHEAD"
SHAPE_COL = "SHAPE@"

class Toolbox(object):
    
    def __init__(self):
        self.label = "WriteMMSIIdPickle"
        self.alias = "WriteMMSIIdPickle"

        # List of tool classes associated with this toolbox
        self.tools = [WriteMMSIIdPickle]

class WriteMMSIIdPickle(object):
    def __init__(self):
        self.label = "WriteMMSIIdPickle"
        self.description = "Convert AIS shipping points to tracks"
        self.canRunInBackground = False

    def updateParameters(self, parameters):
        return


    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True


    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def init_new_track(self):
        new_track = [arcpy.Array(), []]
        return new_track

    def get_shoreline_geometry(self, shoreline_file):
        with arcpy.da.SearchCursor(shoreline_file, ["SHAPE@"]) as cursor:
            for row in cursor:
                return row[0]

    def execute(self, parameters, messages):
        arcpy.AddMessage("starting....")

        arcpy.env.workspace = r"c:\arctic_options_shipping\shipping_points.gdb"

        arcpy.env.overwriteOutput = True
        orig_tracks = {}
        cols = ["mmsi"]

        filename = r"c:\arctic_options_shipping\new_shipping_points.gdb\shipping_points"

        with arcpy.da.SearchCursor(filename, cols) as cursor:
            for row in cursor:
                orig_tracks[row[0]] = row[0]

        outfile = r"c:\arctic_options_shipping\shipping_points\mmsi_id_pickle.txt"
        pickle.dump(orig_tracks, open(outfile, "wb"))


