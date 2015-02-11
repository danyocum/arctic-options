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
        output_dir_wgs = r"c:\arctic_options_shipping\shipping_wgs.gdb"
        output_dir_laea_bering = r"c:\arctic_options_shipping\shipping_laea_bering_hours.gdb"
        wgs_sr = arcpy.SpatialReference(4326)
        arcpy.env.outputCoordinateSystem = wgs_sr
        laea_bering_sr = arcpy.SpatialReference(3571)
        try:
            csv_files = glob.glob(csv_dir)
            fidval = 0

            for fc,csv_file in enumerate(csv_files):
                if fc > 0:
                    return
                gc.collect()
                fid_dict = {}
                filedesc = arcpy.Describe(csv_file)
                basename = filedesc.basename
                arcpy.AddMessage("basename is {}".format(basename))
                i=0
                with codecs.open(csv_file, 'r', encoding='latin-1') as reader:
                    for line in reader:
                        if i == 0:
                            csv_row = line.split(",")
                            for x,attr in enumerate(csv_row):
                                attr = attr.strip()
                                if attr == "timestamp":
                                    timestamp_col = x
                                elif attr == "mmsi":
                                    mmsi_col = x
                                elif attr == "x":
                                    longcol = x
                                elif attr == "y":
                                    latcol = x
                        if i>0:
                            try:
                                csv_row = line.split(",")
                                timeval = csv_row[timestamp_col].strip()
                                mmsival = csv_row[mmsi_col].strip()
                                longval = csv_row[longcol].strip()
                                latval = csv_row[latcol].strip()
                            
                                if float(longval) > 180.0 or float(latval) > 90.0:
                                    arcpy.AddMessage("skipping because of bogus values")
                                    continue
                                    #arcpy.AddMessage("{}".format(csv_row))
                                else:
                                    dt = self.convert_to_time(timeval)
                                    #arcpy.AddMessage("dt: {}".format(dt))
                                    if mmsival is None or mmsival == "0":
                                        continue

                                    new_vals = [dt, timeval, mmsival,longval, latval]
                                    curr_list = fid_dict.get(dt.hour)
                                    if curr_list is not None:
                                        curr_list.extend(new_vals)
                                    else:
                                        curr_list = new_vals
                                    fid_dict[dt.hour] = curr_list

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

                hourkeys = fid_dict.keys()
                hourkeys.sort()
                cols = ["SHAPE@XY", "datetime", "time", "mmsi","long", "lat"]


                for hour in hourkeys:

                    point_list = fid_dict.get(hour)
                    arcpy.AddMessage("for hour {}".format(hour))
                    arcpy.AddMessage("length of list is {}".format(len(point_list)))
                    #arcpy.AddMessage("{}".format(point_list))
                    pts = list(self.chunker(point_list, 5))
                    arcpy.AddMessage("chunked points: ")
                    arcpy.AddMessage("{}".format(pts))
                    if pts is None or len(pts) == 0:
                        arcpy.AddMessage("this hour is empty: {}".format(hour))
                        continue
                    dateinfo = pts[0][0]
 

                    filename = "shipping_{}_{}_{}_{}".format(dateinfo.year, dateinfo.month, dateinfo.day, dateinfo.hour)

                    arcpy.AddMessage("about to write pointfile for {}".format(filename))
                    output_class = arcpy.CreateFeatureclass_management(output_dir_wgs, filename, "POINT")
                    arcpy.AddField_management(output_class, cols[1], "TEXT")
                    arcpy.AddField_management(output_class, cols[2], "TEXT")
                    arcpy.AddField_management(output_class, cols[3], "TEXT")
                    arcpy.AddField_management(output_class, cols[4], "TEXT")
                    arcpy.AddField_management(output_class, cols[5], "TEXT")
                    cols = ["SHAPE@XY", "datetime", "time", "mmsi","long", "lat"]

                    with arcpy.da.InsertCursor(output_class, cols) as cursor:
                        
                        for pcnt,pt in enumerate(pts):
                            try:
                                dt = pt[0]
                                timeval = pt[1]
                                mmsival = pt[2]
                                longval = pt[3]
                                latval = pt[4]
                                pnt = arcpy.Point()
                                pnt.X = float(longval)
                                pnt.Y = float(latval)
                                row = [pnt, str(dt), str(timeval), str(mmsival), str(longval), str(latval)]
            
                                cursor.insertRow(row)
                            except StandardError, e:
                                arcpy.AddMessage("ERROR: {}".format(e))
                                arcpy.AddMessage("pt: {}".format(pt))
                                arcpy.AddMessage("row: {}".format(row))
                                return

                    projected_filename = os.path.join(output_dir_laea_bering, filename)
                    arcpy.AddMessage("projected to laea bering now...")
                    arcpy.Project_management(output_class, projected_filename, laea_bering_sr)


            del fid_dict    
        except StandardError, e:
            arcpy.AddError(e)
        return
    def grouper(self, iterable, n, fillvalue=None):
        args = [iter(iterable)] * n
        return itertools.izip_longest(*args, fillvalue=fillvalue)

    def chunker(self, seq, size):
        return (seq[pos:pos + size] for pos in xrange(0, len(seq), size))

    def convert_to_time(self, timestamp):
        timestamp_arr = timestamp.split(" ")
        datestr = timestamp_arr[0]

        darr = datestr.split("-")
        #arcpy.AddMessage("{}".format(darr))
        year = int(darr[0])
        month = int(darr[1])
        day = int(darr[2])

        timestr = timestamp_arr[1]
        tarr = timestr.split(":")
        #arcpy.AddMessage("{}".format(timestr))
        hour = int(tarr[0])
        minute = int(tarr[1])
        sec = int(tarr[2])

        return_date = datetime.datetime(year, month, day, hour, minute, sec)
        return return_date