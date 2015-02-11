import arcpy
import os
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
        working_dir = r"c:\arctic_options_shipping\shipping_tracks.gdb"
        shoreline_line_file = r"c:\arctic_options_shipping\shoreline.gdb\arctic_full_shoreline_polar_proj_line"
        shoreline_file = r"c:\arctic_options_shipping\shoreline.gdb\arctic_full_shoreline_polar_proj_polygon"
        track_file = r"c:\arctic_options_shipping\shipping_tracks.gdb\ais_tracks_with_shoreline_polar_proj"
        output_track_file = r"c:\arctic_options_shipping\shipping_tracks.gdb\ais_tracks_noland"
        empty_tracks = r"c:\arctic_options_shipping\shipping_tracks.gdb\ais_tracks_empty"
        arcpy.env.workspace = working_dir
        arcpy.env.overwriteOutput = True
        #shoreline_file = os.path.join(working_dir, shoreline_filename)


        arcpy.AddMessage("copying shoreline into memory")
        inmem_shoreline = arcpy.CopyFeatures_management(shoreline_file, r"in_memory\shoreline_inmem")
        inmem_shoreline_line = arcpy.CopyFeatures_management(shoreline_line_file, r"in_memory\shoreline_inmem_line")
        inmem_newtracks = arcpy.CopyFeatures_management(empty_tracks, r"in_memory\empty_tracks")
        #shoreline_file = os.path.join(working_dir, shoreline_filename)
        #track_file = os.path.join(working_dir, track_filename)
        layers = []
        save_trigger = 25
        num_saves = 0
        total_count = -1
        total_rows = 3078

        #if it crashes and we need to restart, make sure this gets set at the right #
        startrow = 0
        with arcpy.da.SearchCursor(track_file, ["OBJECTID"]) as cursor:
            i=0
            for row in cursor:
                
                i+=1

                total_count+=1
                if total_count <= startrow:
                    continue
                objid = row[0]
                where_clause = "OBJECTID = {}".format(objid)
                curr_layer = r"in_memory\tracklayer_{}".format(objid)
                arcpy.AddMessage("creating layer {} of {}".format(total_count, total_rows))
                arcpy.MakeFeatureLayer_management(track_file, curr_layer, where_clause)
                #intsct_results = r"in_memory\int_tracklayer_{}".format(objid)
                #intfeats = [curr_layer, inmem_shoreline]
                arcpy.SelectLayerByLocation_management(curr_layer, "INTERSECT", inmem_shoreline_line, "", "NEW_SELECTION")
                selcount = int(arcpy.GetCount_management(curr_layer).getOutput(0) or 0)
                arcpy.SelectLayerByAttribute_management(curr_layer, "CLEAR_SELECTION")
                
                if selcount > 0:
                    arcpy.AddMessage("erasing....")
                    #erase the shoreline for this layer
                    erased_layer = r"in_memory\erased_lyr_{}".format(objid)
                    arcpy.AddMessage("erasing...")

                    arcpy.Erase_analysis(curr_layer, inmem_shoreline, erased_layer)

                    layers.append(erased_layer)
                else:
                    arcpy.AddMessage("keeping line...")
                    layers.append(curr_layer)

                gc.collect()
                #its long running and arc sometimes crashes, so this saves and resets at new point
                if i >= save_trigger:
                    arcpy.AddMessage("merging...")
                    arcpy.Merge_management(layers, inmem_newtracks)
                    arcpy.AddMessage("!!!!!!!!!!!!!!!!!!!!!!!!!saving tracks to {}".format(output_track_file))
                    arcpy.Append_management(inmem_newtracks, output_track_file)

                    #now reset everything
                    layers = []
                    i=0
                    inmem_newtracks = arcpy.CopyFeatures_management(empty_tracks,r"in_memory\empty_tracks")
                    num_saves+=1
                else:
                    arcpy.AddMessage("i is {} and save_trigger is {}".format(i, save_trigger))

        return
