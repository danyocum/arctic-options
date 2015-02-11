import arcpy
import os
import pickle
import gc
import json

DEBUG=True
#Alaska Albers Equal Area Conic
ALASKA_SR = 102006
#polar projection
POLAR_SR = 7215
ALASKA_EXT= "_alaska"
POLAR_EXT = "_polar"
M_TO_MILES = 6.2137e-4
MMSI_COL = "MMSI"
DATE_COL = "DATE"
NAV_COL = "NAV"
ROT_COL = "ROT"
TIME_COL = "TIME"
TRUEHEAD_COL = "TRUEHEAD"
SHAPE_COL = "SHAPE@"

class Toolbox(object):
    
    def __init__(self):
        self.label = "ReadMMSIIdPickle"
        self.alias = "ReadMMSIIdPickle"

        # List of tool classes associated with this toolbox
        self.tools = [ReadMMSIIdPickle]

class ReadMMSIIdPickle(object):
    def __init__(self):
        self.label = "ReadMMSIIdPickle"
        self.description = "read the id pickle"
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

    def execute(self, parameters, messages):
        arcpy.AddMessage("starting....")
        #the id pickle
        #infile = r"c:\arctic_options_shipping\mmsi_id_pickle.txt"

        #or the id/type pickle
        infile = r"c:\arctic_options_shipping\mmsi_pickle.txt"
        mmsi_ids = pickle.load(open(infile, "rb"))
        #arcpy.AddMessage("{}".format(mmsi_ids))
        
        with open(r'c:\arctic_options_shipping\ship_categories.txt', 'w') as outfile:
                json.dump(ship_types, outfile, sort_keys = True, indent = 4,
                ensure_ascii=False)

        return
        for key, value in mmsi_ids.items():
            found=False
            st = value.get("Ship type")
            for cat, typelist in ship_types.items():
                if st in typelist:
                    arcpy.AddMessage("found {} in category {}".format(st, cat))
                    found=True




ship_types = {"Cargo and Tanker":["Palletised Cargo Ship", "Vegetable Oil Tanker","LPG Tanker", "Cargo ship","Ore/Oil Carrier","LNG Tanker",
        "Crude Oil Tanker", "Cargo ship (HAZ-B)","Vehicles Carrier","Refrigerated Cargo Ship","Chemical/Oil Products Tanker",
        "Tanker","Bulk Carrier", "Passenger/Ro-Ro Cargo Ship","Ro-Ro Cargo Ship","Container Ship","Bulk/Oil Carrier",
        "General Cargo Ship","Oil Products Tanker","Self Discharging Bulk Carrier","Chemical Tanker","Supply Tender","Heavy Load Carrier"],
        "Fishing":["Seal Catcher","Fishing Vessel","Stern Trawler","Trawler","Fishing Support Vessel","Fish Factory Ship", "Fish Carrier",
        "Fishing vessel"],
        "Unknown":["Unknown","WIG","Unknown (HAZ-B)","Vessel (function unknown)", "Other type (HAZ-A)"],
        "Tug":["Port tender","Pusher Tug","Offshore Tug/Supply Ship","Towing vessel","Tug","Towing vessel (tow>200)"], 
        "Working & Support":["Cable Layer","Salvage Ship","Pipe Layer","Crane Ship","Utility Vessel","Anti-polution",
        "Drilling Ship","Offshore Support Vessel","Pollution Control Vessel","Motor Hopper","Pilot","Crew Boat"],
        "Dredging":["Dredging or UW ops","Dredger","Hopper Dredger"],
        "Enforcement and Safety":["Patrol Vessel","Search & Rescue Vessel", "Buoy/Lighthouse Vessel","Standby Safety Vessel","Law enforcment","SAR"],
        "Military":["Military ops"],
        "Diving":["Diving ops"],
        "Sailing":["Sailing Vessel","Sailing vessel"],
        "Passenger & Cruise Ships":["Passenger (Cruise) Ship","Pleasure craft","Passenger/General Cargo Ship","Yacht","Passenger ship",
        "Passenger Ship","HSC"],
        "Research":["Research Survey Vessel","Research Vessel"],
        "Icebreaker":["Icebreaker"],
        "Other":["Landing Craft", "Other type","Local type","Training Ship"]}





















