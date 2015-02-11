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
        cols = ["OBJECTID", "time"]
        #target_time = "2014-10-11 12:59:23"
        x=0
        
        all_dates = self.get_dates()
        #inmem_filename = r"in_memory\shipping_points"
        #arcpy.MakeFeatureLayer_management(filename, inmem_filename)
        with arcpy.da.SearchCursor(filename, cols) as cursor:
            for row in cursor:
                x+=1
                if x % 100000 == 0:
                    arcpy.AddMessage("done with {}".format(x))
                    
                oid = row[0]
                #mmsi = row[1]
                timestamp = row[1]

                rowtime = self.convert_to_time(timestamp)
                #arcpy.AddMessage("rowtime is {}".format(rowtime))
                target_dict = all_dates.get(rowtime.month).get(rowtime.day).get(rowtime.hour)
                target_mmsi_list = target_dict.get(oid)
                if target_mmsi_list:
                    #arcpy.AddMessage("appending to list ")
                    target_mmsi_list.append(oid)
                else:
                    #arcpy.AddMessage("creating new list for {}".format(mmsi))
                    target_dict[oid] = [oid]

        arcpy.AddMessage("working on features...")
        i=0
        year = 2014
        months = all_dates.keys()
        months.sort()
        inmem_filename = None
        for month in months:
            days = all_dates.get(month).keys()
            if inmem_filename is not None:
                del inmem_filename

            inmem_filename = r"in_memory\sp_{}".format(month)
            filename = r"c:\arctic_options_shipping\shipping_points.gdb\shipping_points_{}".format(month)
            arcpy.MakeFeatureLayer_management(filename, inmem_filename)

            days.sort()
            for day in days:
                hour_oid_dict = {}
                hours = all_dates.get(month).get(day).keys()
                hours.sort()
                for hour in hours:
                    hour_oid_dict = {}
                    oid_dicts = all_dates.get(month).get(day).get(hour)
                    oid_values = oid_dicts.keys()
                    oid_values.sort()
                    for oid_val in oid_values: 
                        #uniquify 
                        hour_oid_dict[oid_val] = oid_val

                    oid_wc = self.build_where_clause(hour_oid_dict.keys())
                    if len(hour_oid_dict.keys()) == 0:
                        arcpy.AddMessage("empty oids")
                        continue
                        
                    #curr_lyr = r"in_memory\{}_{}_{}".format(month, day, hour)
                    arcpy.AddMessage("making selection for hour {}-{}-{}: {}".format(year, month, day, hour))
                    #arcpy.AddMessage("with clause of {}".format(oid_wc))
                    arcpy.SelectLayerByAttribute_management(inmem_filename, "NEW_SELECTION", oid_wc)
                    #arcpy.MakeFeatureLayer_management(inmem_filename, curr_lyr, where_clause=oid_wc)
                    #arcpy.AddMessage("copying features for selection of length {}".format(arcpy.GetCount_management(inmem_filename).getOutput(0)))

                    outfile_name = r"c:/arctic_options_shipping/shipping_json.gdb/ship_{}_{}_{}_{}".format(year, month, day, hour)
                    arcpy.CopyFeatures_management(inmem_filename, outfile_name)
                    arcpy.SelectLayerByAttribute_management(inmem_filename, "CLEAR_SELECTION")
                    gc.collect()
                    del hour_oid_dict

                    i+=1

 

    def build_where_clause(self, oid_list):
        wc = ""
        for i, oid in enumerate(oid_list):
            if i == 0:
                wc="{} = {}".format(OBJECTID_KEY, str(oid))
            else:
                wc="{} OR {} = {}".format(wc, OBJECTID_KEY, str(oid))
        return wc

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



