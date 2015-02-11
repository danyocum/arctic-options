import arcpy
import glob
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
        self.label = "MergeErasedTracksToolbox"
        self.alias = "MergeErasedTracksToolbox"

        # List of tool classes associated with this toolbox
        self.tools = [MergeErasedTracks]

class MergeErasedTracks(object):
    
    def __init__(self):
        """Define the tool (PolarToolbox name is the name of the class)."""
        self.label = "MergeErasedTracks"
        self.description = "MergeErasedTracks "
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

        arcpy.env.workspace=r"c:\arctic_options_shipping\erased_tracks.gdb"

        fcs = arcpy.ListFeatureClasses()
            
        output_file = r"c:\arctic_options_shipping\shipping_tracks.gdb\ais_tracks_with_land_erased"
        arcpy.AddMessage("merging {} tracks now".format(len(fcs)))
        arcpy.Merge_management(fcs, output_file)


        return
