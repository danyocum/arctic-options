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
        spatial_ref = arcpy.SpatialReference("WGS 1984 Arctic Polar Stereographic")
        arcpy.env.workspace = r"c:\arctic_options_shipping\new_shipping_points.gdb"

        arcpy.env.overwriteOutput = True
        #point_file = os.path.join(working_dir, point_filename)
        i=0
        orig_tracks = {}
        #cols = ["time", "mmsi","nav","rot","truehead","SHAPE@X", "SHAPE@Y"]
        cols = ["mmsi", "SHAPE@X", "SHAPE@Y","time"]
        #cols = ["time", "mmsi"]
        #filename = r"c:\arctic_options_shipping\shipping_points.gdb\merged_shipping_points"
        filename = r"c:\arctic_options_shipping\new_shipping_points.gdb\shipping_points_arctic_projection"
        i=0
        with arcpy.da.SearchCursor(filename, cols) as cursor:
            for row in cursor:

                i+=1
                mmsi = row[0]
                xloc = row[1]
                yloc = row[2]
                timestamp = row[3]

                if mmsi in orig_tracks:
                    orig_tracks[mmsi] = numpy.append(orig_tracks.get(mmsi), [xloc, yloc, time])
                else:
                    orig_tracks[mmsi] = numpy.array([xloc, yloc, time])

                if i%50000 == 0:
                    arcpy.AddMessage("i is {}".format(i))
        

        arcpy.AddMessage("dumping empty or one point tracks now...")
        tracks = {}
        for key, value in orig_tracks.items():
            if value.size > 3:
                tracks[key] = value

        orig_tracks = None
        gc.collect()

        split_tracks = []
        split_distance = 50000
        #just for counting while dumping output for debugging
        x=0
        #this loop splits the tracks in 2 cases -- by ship id (the outer loop)
        #and if the distance between 2 points is > 20.0 miles
        num_tracks = len(tracks)
        split_tracks = []

        arcpy.AddMessage("number of unsplit files: {}".format(num_tracks))
        
        for mmsi, value_arr in tracks.items():
            x+=1
            curr_track = arcpy.Array()
            prev_point = None
            curr_point = None
            if x%100 == 0:
                arcpy.AddMessage("..................processing track {} of {} for split".format(x, num_tracks))
            
            #new_track = self.init_new_track()
            num_points = len(value_arr)/3
            for curr in range(num_points):
                ptr=curr*3
                shp_x = value_arr[ptr]
                shp_y = value_arr[ptr+1]
                timestamp = value_arr[ptr+2]
                curr_point = arcpy.Point(shp_x, shp_y)

                if self.should_be_split(prev_point, curr_point, split_distance, spatial_ref):
                    #append the old track
                    if curr_track.count > 1:
                        split_tracks.append([mmsi, timestamp, curr_track])
                    
                    #create a new one
                    curr_track = arcpy.Array()

                else:
                    curr_track.append(curr_point)

                prev_point = curr_point

            if curr_track.count > 1:
                split_tracks.append([mmsi, timestamp, curr_track])


        num_tracks = len(split_tracks)
        arcpy.AddMessage("number of split files: {}".format(num_tracks))
        tracks = None

        return

    def should_be_split(self, prev_point, new_point, split_distance, spatial_ref):
        if prev_point is None or new_point is None:
            return False
        else:
            prev_point_geometry = arcpy.PointGeometry(prev_point, spatial_ref)
            new_point_geometry = arcpy.PointGeometry(new_point, spatial_ref)

            dist = prev_point_geometry.distanceTo(new_point_geometry)
    
            #arcpy.AddMessage("distance between points is {}".format(dist))
            return dist > split_distance
