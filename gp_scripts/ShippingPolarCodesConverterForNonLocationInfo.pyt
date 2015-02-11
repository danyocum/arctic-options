import arcpy
import codecs
import datetime
import glob
import itertools
import gc
import os

FIELD_SKETCH_ID = "SC_ID"
DEBUG=True
EFFORT_FIELD = "EFFORT"
SCALED_EFFORT_FIELD = "SC_EFFORT"
BLOCK_ID_FIELD = "BLOCK_ID"

class Toolbox(object):
    
    def __init__(self):
        self.label = "ShippingCodesConverterForNonLocationInfo"
        self.alias = "ShippingCodesConverterForNonLocationInfo"

        # List of tool classes associated with this toolbox
        self.tools = [ShippingCodesConverterForNonLocationInfo]

class ShippingCodesConverterForNonLocationInfo(object):
    
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "ShippingCodesConverterForNonLocationInfo"
        self.description = "read name and type/cargo"
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
        arcpy.env.overwriteOutput = True  
        csv_dir = r"c:\arctic_options_shipping\polar-code-boundary-no-location\*.csv"

        try:
            csv_files = glob.glob(csv_dir)

            for csv_file in csv_files:
                
      
                filedesc = arcpy.Describe(csv_file)
                basename = filedesc.basename
                arcpy.AddMessage("basename is {}".format(basename))

                with codecs.open(csv_file, 'r', encoding='latin-1') as reader:
                    for i, line in enumerate(reader):
                        if i == 0:
                            csv_row = line.split(",")
                            for x,attr in enumerate(csv_row):
                                attr = attr.strip()
                                if attr == "callsign":
                                    callsign_col = x
                                elif attr == "type_and_cargo":
                                    type_col = x
                                elif attr == "mmsi":
                                    mmsi_col = x

                        if i>0:
                            try:
                                csv_row = line.split(",")
                                for x,val in enumerate(csv_row):
                                    arcpy.AddMessage("{}:{}".format(x, val))
                                    
                                callsignval = csv_row[callsign_col].strip()
                                typeval = csv_row[type_col].strip()
                                mmsival = csv_row[mmsi_col].strip()
                                if mmsival is None or len(mmsival.strip()) == 0:
                                    arcpy.AddMessage("emtpy row, skipping...")
                                else:
                                    arcpy.AddMessage("callsign:{};type:{};mmsi:{}".format(callsignval, typeval, mmsival))

                            except StandardError, e:
                                arcpy.AddMessage("soemthing went wrong {}".format(e))
                        if i>50:
                            return

        except StandardError, e:
            arcpy.AddError(e)
        return
