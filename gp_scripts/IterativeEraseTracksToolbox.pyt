import arcpy
import pickle
import time
import os
import gc

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
        #get unique set to erase
        zones_for_track_file = r"c:\arctic_options_shipping\zones_for_tracks_to_erase.txt"

        zones_with_overlap = pickle.load( open(zones_for_track_file, "rb" ))

        #arcpy.AddMessage("working on {}".format(zones_with_overlap))
        track_file = r"c:\arctic_options_shipping\shipping_tracks.gdb\ais_tracks_with_land_overlap"

        starting_gdb = r"c:\arctic_options_shipping\new_fishnet.gdb"
        output_gdb = r"c:\arctic_options_shipping\erased_tracks.gdb"

        num_rows = len(zones_with_overlap)
        i=-1
        objid_keys = zones_with_overlap.keys()
        objid_keys.sort()

        start_zone = 6150
        for objid in objid_keys:
            try:
                i+=1
                if i >= start_zone:
                    
                    zones_to_erase = zones_with_overlap.get(objid)
                    
                    arcpy.AddMessage("erasing {} of {}".format(i, num_rows))
                    track_to_erase_from = r"in_memory\zone_to_erase_{}".format(objid)
                    where_clause = "OBJECTID = {}".format(objid)
                    arcpy.MakeFeatureLayer_management(track_file, track_to_erase_from, where_clause)
                    zones = []
                    for zone_to_erase in zones_to_erase:

                        tgt_layer = "{}\Zone{}".format(starting_gdb,zone_to_erase)
                        if arcpy.Exists(tgt_layer):
                            zones.append(tgt_layer)
                    if len(zones) > 0:
                        
                        merged_zones = r"in_memory\merged_{}".format(objid)
                        if len(zones) == 1:
                            arcpy.AddMessage("using single zone")
                            merged_zones = zones[0]
                        else:
                            
                            arcpy.AddMessage("merging multiple zones...")
                            arcpy.Merge_management(zones, merged_zones)
                            """
                            diss_zones = r"in_memory\dissolved_{}".format(objid)
                            arcpy.Dissolve_management(merged_zones, diss_zones)
                            merged_zones = diss_zones
                            """
                        output_for_track = os.path.join(output_gdb, "track_{}".format(objid))
                        arcpy.AddMessage("repairing geometry...")
                        arcpy.RepairGeometry_management(merged_zones)
                        geom_problem = r"in_memory\geom_prob_{}".format(objid)
                        arcpy.CheckGeometry_management(track_to_erase_from, geom_problem)
                        if int(arcpy.GetCount_management(geom_problem).getOutput(0)) > 0:
                            arcpy.AddMessage("there's a problem with this geometry!!!!")
                            with arcpy.da.SearchCursor(geom_problem, ["*"]) as cursor:
                                for row in cursor:
                                    arcpy.AddMessage("problem row: {}".format(row))
                        else:
                            arcpy.AddMessage("no geometry problems with track!")
                            intsct_data = r"in_memory\intsct_{}".format(objid)
                       
                            arcpy.AddMessage("intersecting zones and track...")
                            arcpy.Clip_analysis(track_to_erase_from, merged_zones, intsct_data, "100 Meters")

                            num_intersects = int(arcpy.GetCount_management(intsct_data).getOutput(0) or 0)
                            arcpy.AddMessage("number of intersects is {}".format(num_intersects))
                            arcpy.AddMessage("about to erase {} from {}".format(zones, objid))
                            arcpy.Erase_analysis(track_to_erase_from, intsct_data, output_for_track, "100 Meters")
                            i+=1

                        arcpy.Delete_management("in_memory")
                        gc.collect()
                else:
                    arcpy.AddMessage("skipping {} with objid {}".format(i, objid))
            except StandardError, e:
                arcpy.AddMessage("SOMETHING WENT WRONG!!")
                arcpy.AddMessage("{}".format(e))
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
