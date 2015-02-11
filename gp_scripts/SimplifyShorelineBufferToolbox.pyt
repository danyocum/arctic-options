import arcpy
import os

DEBUG=True
#Alaska Albers Equal Area Conic
ALASKA_SR = 102006
#polar projection
POLAR_SR = 7215
ALASKA_EXT= "_alaska"
POLAR_EXT = "_polar"
class Toolbox(object):
    
    def __init__(self):
        self.label = "SimplifyShorelineBufferToolbox"
        self.alias = "SimplifyShorelineBufferToolbox"

        # List of tool classes associated with this toolbox
        self.tools = [SimplifyShorelineBuffer]

class SimplifyShorelineBuffer(object):
    
    def __init__(self):
        """Define the tool (PolarToolbox name is the name of the class)."""
        self.label = "SimplifyShorelineBuffer"
        self.description = "Buffer and generalize shoreline "
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
        working_dir = r"c:\arctic_options_shipping\shoreline.gdb"
        shoreline_filename = "arctic_full_shoreline_polar_proj"
        arcpy.env.workspace = working_dir
        arcpy.env.overwriteOutput = True
        arcpy.AddMessage("starting....")
        shoreline_file = os.path.join(working_dir, shoreline_filename)

        arcpy.AddMessage("simplifying polygon now...")
        output_simple = os.path.join(working_dir, shoreline_filename+"_simplified")
        arcpy.cartography.SimplifyPolygon(shoreline_file, output_simple, "POINT_REMOVE", 
            "2000 Meters")
        
        arcpy.AddMessage("simplify complete to {}".format(output_simple))
        return
