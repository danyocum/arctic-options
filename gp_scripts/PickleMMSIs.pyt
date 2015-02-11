import arcpy
import pickle

class Toolbox(object):
    
    def __init__(self):
        self.label = "PickleMMSIs"
        self.alias = "PickleMMSIs"

        # List of tool classes associated with this toolbox
        self.tools = [PickleMMSIs]

class PickleMMSIs(object):
    
    def __init__(self):
        """Define the tool (PolarToolbox name is the name of the class)."""
        self.label = "PickleMMSIs"
        self.description = "PickleMMSIs"
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
        shipping_points = r"C:\arctic_options_shipping\new_shipping_points.gdb\shipping_points"
        mmsis = {}
        with arcpy.da.SearchCursor(shipping_points, ["mmsi"]) as cursor:
            for row in cursor:
                mmsis[row[0]] = row[0]

        arcpy.AddMessage("how many unique mmsids? {}".format(len(mmsis)))
        pickle.dump(mmsis, open(r"C:\arctic_options_shipping\mmsi_id_pickle.txt", "wb"))

        return
