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
        self.label = "ShippingTracksFromPointsToolbox"
        self.alias = "ShippingTracksFromPointsToolbox"

        # List of tool classes associated with this toolbox
        self.tools = [ShippingTracksFromPoints]

class ShippingTracksFromPoints(object):
    def __init__(self):
        self.label = "ShippingTracksFromPoints"
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
        #point_file = os.path.join(working_dir, point_filename)
        orig_tracks = {}
        #cols = ["time", "mmsi","nav","rot","truehead","SHAPE@X", "SHAPE@Y"]
        cols = ["mmsi", "SHAPE@X", "SHAPE@Y","time"]
        #cols = ["time", "mmsi"]
        #filename = r"c:\arctic_options_shipping\shipping_points.gdb\merged_shipping_points"
        filename = r"c:\arctic_options_shipping\new_shipping_points.gdb\shipping_points"
        num_total_rows = int(arcpy.GetCount_management(filename).getOutput(0))
        arcpy.AddMessage("total rows: {}".format(num_total_rows))
        chunk_size = 100000
        num_chunks = int(num_total_rows/chunk_size)
        if num_total_rows % chunk_size != 0:
            num_chunks +=1
            
        for x in range(0,num_chunks):
            orig_tracks = {}
            if x == num_chunks-1:
                startrow = x*chunk_size
                endrow = num_total_rows
            else:
                startrow = (x*chunk_size)
                endrow = startrow+chunk_size

            wc = "OBJECTID >= {} AND OBJECTID < {}".format(startrow, endrow)
            arcpy.AddMessage("wc is {}".format(wc))
            with arcpy.da.SearchCursor(filename, cols, where_clause=wc) as cursor:
                for row in cursor:
                    mmsi = row[0]
                    xloc = row[1]
                    yloc = row[2]
                    timestamp = row[3]
                    if mmsi in orig_tracks:
                        orig_tracks[mmsi] = numpy.append(orig_tracks.get(mmsi), [xloc, yloc, timestamp])
                    else:
                        orig_tracks[mmsi] = numpy.array([xloc, yloc, timestamp])

            arcpy.AddMessage("saving {} items".format(len(orig_tracks)))
            if x == 0:
                testid = "273353470"
                arcpy.AddMessage("for id {} we have:".format(testid))
                arcpy.AddMessage(orig_tracks.get(testid))


            outfilename = r"c:\arctic_options_shipping\shipping_points\shipping_points_pickle"
            outfile = "{}_{}.txt".format(outfilename, x)
            pickle.dump(orig_tracks, open(outfile, "wb"))

            del orig_tracks
            gc.collect()

