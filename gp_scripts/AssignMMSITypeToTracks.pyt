import arcpy
import pickle

SHIP_TYPE_KEY = "Ship type"
class Toolbox(object):
    
    def __init__(self):
        self.label = "AssignMMSITypeToTracks"
        self.alias = "AssignMMSITypeToTracks"

        # List of tool classes associated with this toolbox
        self.tools = [AssignMMSITypeToTracks]

class AssignMMSITypeToTracks(object):
    
    def __init__(self):
        """Define the tool (PolarToolbox name is the name of the class)."""
        self.label = "AssignMMSITypeToTracks"
        self.description = "AssignMMSITypeToTracks"
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

        track_file = r"c:\arctic_options_shipping\shipping_tracks.gdb\all_ais_tracks"
        pickle_file = r"c:\arctic_options_shipping\mmsi_pickle.txt"
        mmsi_type_dict = pickle.load(open(pickle_file, "rb"))
        with arcpy.da.UpdateCursor(track_file, ["MMSI", "type"]) as cursor:
            for row in cursor:
                mmsi_val = row[0]
                val_dict = mmsi_type_dict.get(mmsi_val)
                if val_dict:
                    shiptype = val_dict.get(SHIP_TYPE_KEY)
                    if shiptype is not None:
                        row[1] = shiptype
                        arcpy.AddMessage("found type {} for {}".format(shiptype, mmsi_val))
                        cursor.updateRow(row)
                else:
                    arcpy.AddMessage("no entry found for {}".format(mmsi_val))

        return
