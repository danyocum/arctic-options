import arcpy
import pickle
import time
import os

DEBUG=False
#Alaska Albers Equal Area Conic
ALASKA_SR = 102006
#polar projection
POLAR_SR = 7215
ALASKA_EXT= "_alaska"
POLAR_EXT = "_polar"
SHORE_FCS = []
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
        track_file = r"c:\arctic_options_shipping\shipping_tracks.gdb\ais_tracks_with_land_overlap"
        fishnet_file = r"c:\arctic_options_shipping\arctic_fishnet.shp"
        arcpy.env.overwriteOutput = True
        #zone_fcs = self.build_feature_classes()

        total_rows = int(arcpy.GetCount_management(track_file).getOutput(0))
        arcpy.AddMessage("num total tracks is {}".format(total_rows))

        inmem_tracks = r"in_memory\inmem_tracks"
        arcpy.MakeFeatureLayer_management(track_file, inmem_tracks)

        inmem_fishnet = r"in_memory\inmem_fishnets"
        arcpy.MakeFeatureLayer_management(fishnet_file, inmem_fishnet)

        zones_with_overlap = {}
        i=0
        with arcpy.da.SearchCursor(track_file, ["OBJECTID"]) as cursor:
            for row in cursor:
                objid = row[0]

                curr_zones = []

                where_clause = "OBJECTID = {}".format(objid)
                arcpy.SelectLayerByAttribute_management(inmem_tracks, "NEW_SELECTION", where_clause)
                #start_time = self.print_time(DEBUG, "select by objid", start_time)

                #select by the bounds of the track
                arcpy.SelectLayerByLocation_management(inmem_fishnet, "INTERSECT",inmem_tracks,"", "NEW_SELECTION")
                #start_time = self.print_time(DEBUG, "selecting fishnet", start_time)

                #see which ids are in that layer
                with arcpy.da.SearchCursor(inmem_fishnet, ["splid"]) as cursor:
                    for row in cursor:
                        splid = row[0][4:]
                        curr_zones.append(splid)

                #start_time = self.print_time(DEBUG, "done with searching new layer", start_time)
                arcpy.SelectLayerByAttribute_management(inmem_fishnet, "CLEAR_SELECTION")
                arcpy.SelectLayerByAttribute_management(inmem_tracks, "CLEAR_SELECTION")
                #start_time = self.print_time(DEBUG, "clearing selection ", start_time)
                if len(curr_zones) > 0:
                    zones_with_overlap[objid] = curr_zones

                i+=1
                if i%100 == 0:
                    arcpy.AddMessage("finished with {}".format(objid))

        #get unique set to erase
        zones_for_track_file = r"c:\arctic_options_shipping\zones_for_tracks_to_erase.txt"

        pickle.dump(zones_with_overlap, open(zones_for_track_file, "wb" ))
        return




    def build_feature_classes(self):
        fcs= {}
        starting_gdb = r"c:\arctic_options_shipping\fishnet.gdb"
        arcpy.AddMessage("starting feature layer read....")
        for x in range(1,401):
            try:
                lyr = r"in_memory\shoreline_{}".format(x)
                tgt_layer = "{}\Zone{}".format(starting_gdb,x)
                if arcpy.Exists(tgt_layer):
                    arcpy.MakeFeatureLayer_management(tgt_layer, lyr)
                    fcs[x] = lyr
            except StandardError, e:
                arcpy.AddMessage("skipping for error: {}".format(e))


        arcpy.AddMessage("layer read finished.")
        return fcs



    def get_zones_to_erase(self, track_lyr, lyr_dict, curr_count):
        start_time = time.time()
        num_zones_with_overlap = {}
        selcount = 0
        for zone_num, lyr in lyr_dict.items():
            start_time = time.time()
            feats = [track_lyr, lyr]
            out_intsct = r"in_memory\out_lyr"
            arcpy.Intersect_analysis(feats, out_intsct)
            start_time = self.print_time(DEBUG, "intersect took ", start_time)
            arcpy.SelectLayerByLocation_management(lyr, "INTERSECT", track_lyr, "", "NEW_SELECTION")
            start_time = self.print_time(DEBUG, "selection took", start_time)
            selcount = int(arcpy.GetCount_management(track_lyr).getOutput(0) or 0)
            start_time = self.print_time(DEBUG, "getCount took ", start_time)
            

            if selcount > 0:
                num_zones_with_overlap[zone_num] = zone_num

        #start_time = self.print_time(DEBUG, "selection took ", start_time)
        return num_zones_with_overlap
