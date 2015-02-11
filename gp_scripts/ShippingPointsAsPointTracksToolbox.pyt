import arcpy
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
TIME_FIELD = "time"
OID_FIELD = "OBJECTID"
ORIG_OID_FIELD = "ORIG_OID"

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
        cols = [ "mmsi", "SHAPE@X", "SHAPE@Y",OID_FIELD]
        filename = r"c:\arctic_options_shipping\new_shipping_points.gdb\shipping_points"
        i=0
        orig_tracks = {}
        sample_mmsi = None
        with arcpy.da.SearchCursor(filename, cols) as cursor:
            for row in cursor:
                i+=1
                mmsi = row[0]
                xloc = row[1]
                yloc = row[2]
                oid = int(row[3])
                if mmsi == "0":
                    #arcpy.AddMessage("MMSI of 0")
                    continue
                if mmsi in orig_tracks:
                    orig_tracks[mmsi] = numpy.append(orig_tracks.get(mmsi), [xloc, yloc, oid])
                else:
                    orig_tracks[mmsi] = numpy.array([xloc, yloc, oid])

                if (i % 50000) == 0:
                    arcpy.AddMessage("processed {}".format(i))

        gc.collect()
        
        split_tracks = []
        #split_distance = 50000
        #just for counting while dumping output for debugging
        x=0
        #this loop splits the tracks in 2 cases -- by ship id (the outer loop)
        #and if the distance between 2 points is > 20.0 miles
        num_tracks = len(orig_tracks)
        split_tracks = []

        arcpy.AddMessage("number of unsplit files: {}".format(num_tracks))
        
        for mmsi, value_arr in orig_tracks.items():
            x+=1
            curr_track = []
            #prev_point = None
            curr_point = None
            if x%10 == 0:
                arcpy.AddMessage("..................processing track {} of {} for split".format(x, num_tracks))
            
            num_points = len(value_arr)/3
            for curr in range(num_points):
                ptr=curr*3
                shp_x = value_arr[ptr]
                shp_y = value_arr[ptr+1]
                original_oid = int(value_arr[ptr+2])
                curr_point = arcpy.Point(shp_x, shp_y)
                """
                if self.should_be_split(prev_point, curr_point, split_distance, spatial_ref):
                    #append the old track
                    if curr_track.count > 1:
                        split_tracks.append([mmsi, original_oid, curr_track])

                    #create a new one
                    curr_track = []
                else:
                    curr_track.append(curr_point)
                """
                if curr_point is not None:
                    curr_track.append([original_oid, curr_point])

                #prev_point = curr_point

            
            split_tracks.append([mmsi, curr_track])
        
        del orig_tracks
        gc.collect()
        """
        for x in range(0,95):
            if len(split_tracks[x]) > 1:
                arcpy.AddMessage("{}".format(split_tracks[x]))
        return
        """
        points_trackfile = self.write_point_tracks(split_tracks)

        gc.collect()

        #now write the timestamp with original oid
        self.write_timestamp(filename, points_trackfile)

    def write_timestamp(self, orig_points_filename, points_trackfile):

        timestamp_by_oid = {}

        arcpy.AddMessage("building dictionary of timestamps for original object ids")
        i=0
        with arcpy.da.SearchCursor(orig_points_filename, [OID_FIELD, TIME_FIELD]) as cursor:
            for row in cursor:
                i+=1
                timestamp_by_oid[int(row[0])] = row[1]
                if i%50000 == 0:
                    arcpy.AddMessage('finished building dictionary for {}'.format(i))

        arcpy.AddField_management(points_trackfile, TIME_FIELD, "TEXT")

        i=0
        with arcpy.da.UpdateCursor(points_trackfile, [ORIG_OID_FIELD, TIME_FIELD]) as cursor:
            for row in cursor:
                i+=1
                if i%50000 == 0:
                    arcpy.AddMessage("finished adding timestamp for {}".format(i))
                oid = int(row[0])
                timestamp = timestamp_by_oid.get(oid)
                row[1] = timestamp
                cursor.updateRow(row)
 


    def write_point_tracks(self, split_tracks):

        output_dir = r"c:\arctic_options_shipping\shipping_points.gdb"
        cols = [ "mmsi",ORIG_OID_FIELD, "pnt"]

        class_name = "tracks_as_points_with_oid"
        output_class = arcpy.CreateFeatureclass_management(output_dir, class_name, "POINT")
        arcpy.AddField_management(output_class, cols[0], "TEXT")
        arcpy.AddField_management(output_class, cols[1], "TEXT")
        arcpy.AddField_management(output_class, cols[2], "TEXT")


        arcpy.AddMessage("------------------------------------  about to insert {} rows".format(len(split_tracks)))
        cols.append("SHAPE@XY")

        with arcpy.da.InsertCursor(output_class, cols) as cursor:
            try:
                
                for track in split_tracks:
                    mmsi = track[0]
                    for x, point_arr in enumerate(track[2]):
                        original_oid = point_arr[0]
                        point = point_arr[1]
                        row = [mmsi, original_oid, x, point]
                        cursor.insertRow(row)
            except StandardError, e:
                arcpy.AddMessage("ERROR: skipping {}".format(e))

        arcpy.AddMessage("reprojecting to polar")
        polar_sr = arcpy.SpatialReference("WGS 1984 Arctic Polar Stereographic")
        #output_repro = r"c:\arctic_options_shipping\shipping_points.gdb\tracks_as_points_polar"
        #arcpy.Project_management(output_class, output_repro, polar_sr)
        arcpy.DefineProjection_management(output_class, polar_sr)

        return output_class

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
