import arcpy
import codecs
import os
import glob


FIELD_SKETCH_ID = "SC_ID"
DEBUG=True
EFFORT_FIELD = "EFFORT"
SCALED_EFFORT_FIELD = "SC_EFFORT"
BLOCK_ID_FIELD = "BLOCK_ID"

class Toolbox(object):
    
    def __init__(self):
        self.label = "ShippingConverter"
        self.alias = "ShippingConverter"

        # List of tool classes associated with this toolbox
        self.tools = [ShippingConverter]

class ShippingConverter(object):
    
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "ShippingConverter"
        self.description = "Calculate the effort"
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
        #mile_conversion = 1.1508
        arcpy.env.overwriteOutput = True  
        csv_dir = r"c:\arctic_options_shipping\Polar Boundary Codes\*.csv"
        output_dir = r"c:\arctic_options_shipping\shipping_points.gdb"
        try:
            csv_files = glob.glob(csv_dir)
            fidval = 0
            for csv_file in csv_files:
                fid_dict = {}
                filedesc = arcpy.Describe(csv_file)
                basename = filedesc.basename
                arcpy.AddMessage("basename is {}".format(basename))
                i=0
                reader = codecs.open(csv_file, 'r', encoding='latin-1')
                for line in reader:
                    if i == 0:
                        csv_row = line.split(",")
                        for x,attr in enumerate(csv_row):
                            attr = attr.strip()
                            if attr == "timestamp":
                                timestamp_col = x
                            elif attr == "mmsi":
                                mmsi_col = x
                            elif attr == "nav_status":
                                nav_status_col = x
                            elif attr == "x":
                                longcol = x
                            elif attr == "y":
                                latcol = x
                            elif attr == "rot":
                                rot_col = x
                            elif attr == "true_heading":
                                true_heading_col = x

                    if i>0:
                        try:
                            csv_row = line.split(",")

                            timeval = csv_row[timestamp_col].strip()
                            mmsival = csv_row[mmsi_col].strip()
                            navval = csv_row[nav_status_col].strip()
                            rotval = csv_row[rot_col].strip()
                            trueheadingval = csv_row[true_heading_col].strip()

                            longval = csv_row[longcol].strip()
                            latval = csv_row[latcol].strip()
                        
                            if float(longval) > 180.0 or float(latval) > 90.0:
                                arcpy.AddMessage("skipping because of bogus values")
                                continue
                                #arcpy.AddMessage("{}".format(csv_row))
                            else:
                                fid_dict[fidval] = [timeval,  mmsival, navval, rotval,trueheadingval, longval, latval]

                        except StandardError, e:
                            arcpy.AddMessage("-----------------------------------------------------  problem: {};length:{}".format(e, len(csv_row)))
                            arcpy.AddMessage("csvfile: {}".format(csv_file))
                            arcpy.AddMessage("mmsid: {}".format(mmsival))
                            arcpy.AddMessage("{}".format(csv_row))
                            arcpy.AddMessage("long:{}; lat:{}".format(longval, latval))

                        fidval+=1
                    i+=1

                arcpy.AddMessage("done parsing: {}".format(csv_file))
                #polar_sr = arcpy.SpatialReference("WGS 1984 Arctic Polar Stereographic")
                wgs_sr = arcpy.SpatialReference(4326)
                arcpy.env.outputCoordinateSystem = wgs_sr
                cols = ["time", "mmsi","nav","rot","truehead","long", "lat"]

                output_class = arcpy.CreateFeatureclass_management(output_dir, basename.replace('-','_'), "POINT")
                arcpy.AddField_management(output_class, cols[0], "TEXT")
                arcpy.AddField_management(output_class, cols[1], "TEXT")
                arcpy.AddField_management(output_class, cols[2], "TEXT")
                arcpy.AddField_management(output_class, cols[3], "TEXT")
                arcpy.AddField_management(output_class, cols[4], "TEXT")
                arcpy.AddField_management(output_class, cols[5], "TEXT")
                arcpy.AddField_management(output_class, cols[6], "TEXT")       

                arcpy.AddMessage("about to insert {} rows".format(len(fid_dict)))
                cols.append("SHAPE@XY")

                with arcpy.da.InsertCursor(output_class, cols) as cursor:
                    try:
                        for key,val in fid_dict.items():
                            pnt = arcpy.Point()
                            pnt.X = float(val[5])
                            pnt.Y = float(val[6])

                            row = [str(val[0]), str(val[1]), str(val[2]), str(val[3]), str(val[4]), 
                                    str(val[5]), str(val[6]), pnt]
                            cursor.insertRow(row)
                    except StandardError, e:
                        arcpy.AddMessage("ERROR: skipping {} because {}".format(key, e))

        except StandardError, e:
            arcpy.AddError(e)
        return
