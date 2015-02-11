import numpy
import arcpy
import glob


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
        seaice_rasters = glob.glob(raster_dir)
        """
        sr = arcpy.SpatialReference(POLAR_SR)
        for i, rast in enumerate(seaice_rasters):
            arcpy.AddMessage("defining projection for {}".format(rast))
            arcpy.DefineProjection_management(rast, sr)
        """
        raster_arrays = []
        for i, rast in enumerate(seaice_rasters):
            if i == 0:
                

            arcpy.AddMessage("working on {}".format(i))
            arr = arcpy.RasterToNumPyArray(rast)
            raster_arrays.append(arr)

        arcpy.AddMessage("calculating mean")
        #arcpy.env.outCoordinateSystem = sr
        mean_raster_arr = numpy.mean(raster_arrays, axis=0)
        arcpy.AddMessage("writing mean raster")
        mean_raster = arcpy.NumPyArrayToRaster(mean_raster_arr,ll,dsc.meanCellWidth,dsc.meanCellHeight)
        mean_raster.save(r"c:\arctic_options_shipping\mean_seaice_raster.tif")

        return
