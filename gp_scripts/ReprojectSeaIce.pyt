import numpy
import arcpy
import glob
import os

DEBUG=True
POLAR_SR = 7215
class Toolbox(object):
    
    def __init__(self):
        self.label = "CalcSeaIceAverage"
        self.alias = "CalcSeaIceAverage"

        # List of tool classes associated with this toolbox
        self.tools = [CalcSeaIceAverage]

class CalcSeaIceAverage(object):
    
    def __init__(self):
        """Define the tool (PolarToolbox name is the name of the class)."""
        self.label = "CalcSeaIceAverage"
        self.description = "CalcSeaIceAverage"
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
        raster_dir = r"C:\arctic_options_shipping\seaice\rasters\2013\*.tif"
        output_dir = r"C:\arctic_options_shipping\seaice\repro_rasters\2013"

        seaice_rasters = glob.glob(raster_dir)
        #sr = arcpy.SpatialReference(3572)
        sr = arcpy.Describe(r"C:\arctic_options_shipping\shipping_laea_bering.gdb\shipping_2014_10_1_0").spatialReference
        arcpy.AddMessage("spatial ref: {}".format(sr))
        return
        
        for i, rast in enumerate(seaice_rasters):
           
            base = os.path.basename(rast)
            
            outname = os.path.join(output_dir, base)

            arcpy.AddMessage("reprojecting to {}".format(outname))
            arcpy.ProjectRaster_management(rast, outname, sr) 

            
        return
