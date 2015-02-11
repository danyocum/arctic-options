import arcpy
import gc
import pickle

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

    def get_erase_dict(self):
        erase_pickle = r"c:\arctic_options_shipping\erase_overlap_values.txt"
        return pickle.load(open(erase_pickle, 'rb'))

    def execute(self, parameters, messages):
        working_dir = r"c:\arctic_options_shipping\shipping_tracks.gdb"

        shoreline_file = r"c:\arctic_options_shipping\simple_shoreline.gdb\arctic_shoreline_simplified"
        track_file = r"c:\arctic_options_shipping\shipping_tracks.gdb\ais_tracks_with_land_overlap"

        output_track_file = r"c:\arctic_options_shipping\shipping_tracks.gdb\ais_tracks_land_erased"
        empty_tracks = r"c:\arctic_options_shipping\shipping_tracks.gdb\ais_tracks_empty"
        arcpy.env.workspace = working_dir
        arcpy.env.overwriteOutput = True

        inmem_newtracks = arcpy.CopyFeatures_management(empty_tracks, r"in_memory\empty_tracks")

        layers = []
        save_trigger = 100
        total_count = -1
        # total_rows = len(arcpy.GetCount_management(track_file).getOutput(0))
        total_rows = 25242

        erase_dict = self.get_erase_dict()
        arcpy.AddMessage("{}".format(erase_dict))
        return

        #if it crashes and we need to restart, make sure this gets set at the right #
        startrow = 0
        with arcpy.da.SearchCursor(track_file, ["OBJECTID"]) as cursor:
            i=0
            for row in cursor:
                i+=1
                total_count+=1
                if total_count >= startrow:
                    objid = row[0]
                    where_clause = "OBJECTID = {}".format(objid)
                    curr_layer = r"in_memory\tracklayer_{}".format(objid)
                    arcpy.AddMessage("creating layer {} of {}".format(total_count, total_rows))

                    arcpy.MakeFeatureLayer_management(track_file, curr_layer, where_clause)
                    erased_layer = r"in_memory\erased_lyr_{}".format(objid)

                    erased_layer = self.erase_tiles(curr_layer, erase_dict, total_count)
                    layers.append(erased_layer)

                    #its long running and arc sometimes crashes, so this saves and resets at new point
                    if i >= save_trigger:

                        arcpy.Merge_management(layers, inmem_newtracks)
                        arcpy.Append_management(inmem_newtracks, output_track_file)
                        arcpy.Delete_management(inmem_newtracks)


                        inmem_newtracks = arcpy.CopyFeatures_management(empty_tracks,r"in_memory\empty_tracks")
                        #inmem_shoreline = arcpy.CopyFeatures_management(shoreline_file, r"in_memory\shoreline_inmem")
                        #now reset everything
                        layers = []
                        i=0
                        gc.collect()


        return

    def erase_tiles(self, curr_layer, erase_dict, objid):
        arcpy.AddMessage("object id: {}".format(objid))
        zones = erase_dict.get(objid)
        for zone in zones:
            arcpy.AddMessage("{}".format(zone))

        #arcpy.Erase_analysis(curr_layer, erased_layer)
        #num_after_erase = int(arcpy.GetCount_management(erased_layer).getOutput(0) or 0)
