
import arcpy
import glob
import os
import numpy

DEBUG=True
POLAR_SR = 7215
class Toolbox(object):
    
    def __init__(self):
        self.label = "MassageSeaIce"
        self.alias = "MassageSeaIce"

        # List of tool classes associated with this toolbox
        self.tools = [MassageSeaIce]

class MassageSeaIce(object):
    
    def __init__(self):
        """Define the tool (PolarToolbox name is the name of the class)."""
        self.label = "MassageSeaIce"
        self.description = "MassageSeaIce"
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
        output_dir = r"C:\arctic_options_shipping\seaice\rep"
        final_output_dir = output_dir = r"C:\arctic_options_shipping\seaice\final"
        png_dir = output_dir = r"C:\arctic_options_shipping\seaice\working"
        base_symbology_lyr = r"C:\arctic_options_shipping\seaice\symbology.png"
        base_symbology_clr = r"C:\arctic_options_shipping\seaice\symbology.clr"
        seaice_rasters = glob.glob(raster_dir)

        sr = arcpy.Describe(r"C:\arctic_options_shipping\shipping_laea_alaska_3572.gdb\shipping_2014_7_1_1").spatialReference

        num_rasts = len(seaice_rasters)
        for i, rast in enumerate(seaice_rasters):

            arcpy.AddMessage("working on {} of {}....".format(i, num_rasts))

            base = os.path.basename(rast)
            outname = os.path.join(output_dir, "rep_"+base)
            raster_desc = arcpy.Describe(rast)
            basename = raster_desc.baseName
        
            arcpy.ProjectRaster_management(rast, outname, sr, "", 25000) 

            inraster =arcpy.sa.Raster(outname)
            #arcpy.sa.Con(inraster > 250,0,inraster)
            outrast = arcpy.sa.Con(inraster < 0.01,0,inraster)
            outrast = arcpy.sa.Con(outrast < 250,(outrast/250*100),0)

            outrast.save(outname)
            tif_outname = os.path.join(png_dir, basename+".simple.tif")
            png_simple_outname = os.path.join(final_output_dir, basename+".png")

            arcpy.CopyRaster_management(outname, tif_outname,"",0,0,"NONE","NONE", "8_BIT_SIGNED", "NONE", "NONE")
            arcpy.AddColormap_management(tif_outname, "", base_symbology_clr)
           
            arcpy.CopyRaster_management(tif_outname, png_simple_outname, "#", 0, 0, "NONE", "NONE", "#", "NONE", "NONE")
           
            
            
        
        return
