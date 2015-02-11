import arcpy
import os
import pickle
import gc
import numpy
import glob

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
        arcpy.env.workspace = r"c:\arctic_options_shipping\shipping_points.gdb"
        arcpy.env.overwriteOutput = True

        point_pickles = glob.glob(r"c:\arctic_options_shipping\shipping_points\*.txt")

        for pp_cnt,pp in enumerate(point_pickles):
            arcpy.AddMessage("loading {}".format(pp))
            orig_tracks = pickle.load(open(pp, "rb"))

            arcpy.AddMessage("total number of orig_tracks is {}".format(len(orig_tracks)))
            tracks = {}
            for key, value in orig_tracks.items():
                if value.size > 3:
                    tracks[key] = value

            del orig_tracks
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
                        curr_track = []
                    else:
                        curr_track.append(curr_point)

                    prev_point = curr_point

                if curr_track.count > 1:
                    split_tracks.append([mmsi, timestamp, curr_track])


            num_tracks = len(split_tracks)
            arcpy.AddMessage("number of split files: {}".format(num_tracks))
            tracks = None
            self.write_point_tracks(split_tracks, pp_cnt)

            del split_tracks
            gc.collect()

    def write_point_tracks(self, split_tracks, pp_cnt):
        output_dir = r"c:\arctic_options_shipping\shipping_points.gdb"
        cols = [ "mmsi","time", "pnt"]

        class_name = "tracks_as_points_{}".format(pp_cnt)
        output_class = arcpy.CreateFeatureclass_management(output_dir, class_name, "POINT")
        arcpy.AddField_management(output_class, cols[0], "TEXT")
        arcpy.AddField_management(output_class, cols[1], "TEXT")
        arcpy.AddField_management(output_class, cols[2], "TEXT")


        arcpy.AddMessage("about to insert {} rows".format(len(split_tracks)))
        cols.append("SHAPE@XY")


        with arcpy.da.InsertCursor(output_class, cols) as cursor:
            try:
                
                for track in split_tracks:
                    arcpy.AddMessage("{}".format(track))
                    mmsi = track[0]
                    time = track[1]
                    for x, point in enumerate(track[2]):
                        row = [mmsi, time, x, point]
                        cursor.insertRow(row)
            except StandardError, e:
                arcpy.AddMessage("ERROR: skipping {}".format(e))

        arcpy.AddMessage("reprojecting to polar")
        polar_sr = arcpy.SpatialReference("WGS 1984 Arctic Polar Stereographic")
        #output_repro = r"c:\arctic_options_shipping\shipping_points.gdb\tracks_as_points_polar"
        #arcpy.Project_management(output_class, output_repro, polar_sr)
        arcpy.DefineProjection_management(output_class, polar_sr)


    def should_be_split(self, prev_point, new_point, split_distance, spatial_ref):
        if prev_point is None or new_point is None:
            return False
        else:
            prev_point_geometry = arcpy.PointGeometry(prev_point, spatial_ref)
            new_point_geometry = arcpy.PointGeometry(new_point, spatial_ref)

            dist = prev_point_geometry.distanceTo(new_point_geometry)
    
            del prev_point_geometry
            del new_point_geometry
            gc.collect()
            #arcpy.AddMessage("distance between points is {}".format(dist))
            return dist > split_distance
