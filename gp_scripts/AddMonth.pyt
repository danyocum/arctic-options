import arcpy
import gc
import datetime
OBJECTID_KEY = "OBJECTID"


class Toolbox(object):
    
    def __init__(self):
        self.label = "ExtractMMSIByTime"
        self.alias = "ExtractMMSIByTime"

        # List of tool classes associated with this toolbox
        self.tools = [ShippingTracksFromPoints]

class ShippingTracksFromPoints(object):
    def __init__(self):
        self.label = "ExtractMMSIByTime"
        self.description = "Convert AIS shipping points to tracks"
        self.canRunInBackground = False

    def updateParameters(self, parameters):
        return


    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True


    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def init_new_track(self):
        new_track = [arcpy.Array(), []]
        return new_track

    def get_shoreline_geometry(self, shoreline_file):
        with arcpy.da.SearchCursor(shoreline_file, ["SHAPE@"]) as cursor:
            for row in cursor:
                return row[0]

    def get_dates(self):
        year = 2014
        months = {7:31,8:31,9:30,10:31}
        all_dates = {}
        mo_vals = months.keys()
        mo_vals.sort()
        for mo in mo_vals:
            days = months.get(mo)
            all_dates[mo] = {}
            for day in range(1,days+1):
                #for hour in range(0,24):
                all_dates[mo][day] = {}
                for hr in range(0,24):
                    all_dates[mo][day][hr] = {}

        #arcpy.AddMessage('{}'.format(all_dates))
        return all_dates

    def execute(self, parameters, messages):
        filename = r"c:\arctic_options_shipping\shipping_points.gdb\shipping_points"
        cols = ["OBJECTID", "time", "month"]
        #inmem_filename = r"in_memory\shipping_points"
        #arcpy.MakeFeatureLayer_management(filename, inmem_filename)

        with arcpy.da.UpdateCursor(filename, cols) as cursor:
            for row in cursor:
                timestamp = row[1]
                rowtime = self.convert_to_time(timestamp)
                row[2] = rowtime.month
                cursor.updateRow(row)

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
