import arcpy

import os
import json


class Toolbox(object):
    
    def __init__(self):
        self.label = "ShippingConverter"
        self.alias = "ShippingConverter"

        # List of tool classes associated with this toolbox
        self.tools = [ConvertToGeoJSON]

class ConvertToGeoJSON(object):
    
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "ConvertToGeoJSON"
        self.description = "Calculate"
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
        feature_dir = r"c:\arctic_options_shipping\shipping_laea_bering.gdb"
        arcpy.env.workspace = feature_dir

        try:
            feature_files = arcpy.ListFeatureClasses()
            
            output_dir = r"c:\arctic_options_shipping\geojson_output2"
            if not os.path.exists(output_dir):
                os.mkdir(output_dir)

            num_files = len(feature_files)
            for x, ff in enumerate(feature_files):
                arcpy.SetProgressor("step", "Working on feature file ", x, num_files)

                arcpy.AddMessage("working on {} of {}".format(x, num_files))
                ffdesc = arcpy.Describe(ff)
                output_filename = os.path.join(output_dir, ffdesc.baseName+".json")
                self.write_geojson_file(ff, output_filename)

        except StandardError, e:
            arcpy.AddError(e)
        return

    def part_split_at_nones(self, part_items):
        current_part = []
        for item in part_items:
            if item is None:
                if current_part:
                    yield current_part
                current_part = []
            else:
                current_part.append((item.X, item.Y))
        if current_part:
            yield current_part

    def geometry_to_struct(self, in_geometry):
        if in_geometry is None:
            return None
        elif isinstance(in_geometry, arcpy.PointGeometry):
            pt = in_geometry.getPart(0)
            return {
                        'type': "Point",
                        'coordinates': (pt.X, pt.Y)
                   }
        elif isinstance(in_geometry, arcpy.Polyline):
            parts = [[(point.X, point.Y) for point in in_geometry.getPart(part)]
                     for part in xrange(in_geometry.partCount)]
            if len(parts) == 1:
                return {
                            'type': "LineString",
                            'coordinates': parts[0]
                       }
            else:
                return {
                            'type': "MultiLineString",
                            'coordinates': parts
                       }
        elif isinstance(in_geometry, arcpy.Polygon):
            parts = [list(self.part_split_at_nones(in_geometry.getPart(part)))
                     for part in xrange(in_geometry.partCount)]
            if len(parts) == 1:
                return {
                            'type': "Polygon",
                            'coordinates': parts[0]
                       }
            else:
                return {
                            'type': "MultiPolygon",
                            'coordinates': parts
                       }
        else:
            raise ValueError(in_geometry)


    def geojson_lines_for_feature_class(self, in_feature):


        aliased_fields = {}
        in_feature_class = r"in_memory\shape"
        arcpy.MakeFeatureLayer_management(in_feature, in_feature_class)
        shape_field = arcpy.Describe(in_feature_class).shapeFieldName
        
        
        lf = arcpy.ListFields(in_feature_class)
        for field in lf:
            aliased_fields[field.name] = field


        spatial_reference = arcpy.SpatialReference(3572)
        record_count = int(arcpy.management.GetCount(in_feature_class).getOutput(0))

        with arcpy.da.SearchCursor(in_feature_class, ['SHAPE@', '*'],
                                   spatial_reference=spatial_reference) as in_cur:
            #col_names = [aliased_fields.get(f, f) for f in in_cur.fields[1:]]
            col_names = in_cur.fields[1:]
            
            yield '{'
            yield '  "type": "FeatureCollection",'
            yield '  "features": ['
            for row_idx, row in enumerate(in_cur):
                if row_idx:
                    yield "    ,"
                if (row_idx % 100 == 1):
                    arcpy.SetProgressorPosition(row_idx)
                geometry_dict = self.geometry_to_struct(row[0])
                property_dict = dict(zip(col_names, row[1:]))
                if shape_field in property_dict:
                    del property_dict[shape_field]
                row_struct = {
                                "type": "Feature",
                                "geometry": geometry_dict,
                                "properties": property_dict
                             }
                for line in json.dumps(row_struct, indent=2).split("\n"):
                    yield "    " + line
            yield '  ]'
            yield '}'

    def get_geojson_string(self, in_feature_class):
        return "\n".join(self.geojson_lines_for_feature_class(in_feature_class))

    def write_geojson_file(self, in_feature_class, out_json_file):
        arcpy.AddMessage("Writing features from {} to {}".format(in_feature_class,
                                                                 out_json_file))
        with open(out_json_file, 'wb') as out_json:
            for line in self.geojson_lines_for_feature_class(in_feature_class):
                out_json.write(line + "\n")
