import arcpy
import os
import re

def update_geodatabase(workspace, output_gdb, feature_class_name, geom_type, id_field_name="SOATO", id_field_length=4):
    """
    Updates the geodatabase feature class by synchronizing it with new shapefiles in a given directory.

    Args:
        workspace (str): Path to the folder with shapefiles.
        output_gdb (str): Path to the file geodatabase.
        feature_class_name (str): Name of the target feature class inside the geodatabase.
        geom_type (str): Geometry type of input shapefiles ("POLYGON", "POINT", "POLYLINE").
        id_field_name (str): Name of the identifier field. Default is "SOATO".
        id_field_length (int): Length of the identifier field. Default is 4.
    """

    if not arcpy.Exists(output_gdb):
        arcpy.CreateFileGDB_management(os.path.dirname(output_gdb), os.path.basename(output_gdb))

    feature_class_path = os.path.join(output_gdb, feature_class_name)
    arcpy.env.workspace = workspace

    shapefiles = arcpy.ListFeatureClasses("*.shp", geom_type)

    def clean_filename(name):
        return re.sub(r'\W+', '_', name)[:50]

    temp_layers = []

    for shp in shapefiles:
        name = os.path.splitext(os.path.basename(shp))[0]
        id_value = name[1:-3]
        clean_name = clean_filename(name)

        temp_fc = arcpy.FeatureClassToFeatureClass_conversion(shp, "in_memory", clean_name)
        arcpy.AddField_management(temp_fc, id_field_name, "TEXT", field_length=id_field_length)

        with arcpy.da.UpdateCursor(temp_fc, id_field_name) as cursor:
            for row in cursor:
                row[0] = id_value
                cursor.updateRow(row)

        temp_layers.append(temp_fc)

    merged_fc = "in_memory/merged_temp_layer"
    arcpy.Merge_management(temp_layers, merged_fc)

    if arcpy.Exists(feature_class_path):
        existing_ids = {row[0] for row in arcpy.da.SearchCursor(feature_class_path, id_field_name)}
        new_ids = {row[0] for row in arcpy.da.SearchCursor(merged_fc, id_field_name)}

        ids_to_delete = existing_ids - new_ids
        if ids_to_delete:
            with arcpy.da.UpdateCursor(feature_class_path, id_field_name) as cursor:
                for row in cursor:
                    if row[0] in ids_to_delete:
                        cursor.deleteRow()

        with arcpy.da.UpdateCursor(feature_class_path, [id_field_name, "SHAPE@"]) as cursor:
            for row in cursor:
                if row[0] in new_ids:
                    new_shape = next(arcpy.da.SearchCursor(merged_fc, ["SHAPE@"], f"{id_field_name} = '{row[0]}'"))[0]
                    if row[1] != new_shape:
                        row[1] = new_shape
                        cursor.updateRow(row)

        ids_to_add = new_ids - existing_ids
        if ids_to_add:
            with arcpy.da.InsertCursor(feature_class_path, [id_field_name, "SHAPE@"]) as cursor:
                for id_value in ids_to_add:
                    new_shape = next(arcpy.da.SearchCursor(merged_fc, ["SHAPE@"], f"{id_field_name} = '{id_value}'"))[0]
                    cursor.insertRow([id_value, new_shape])

        print(f"Feature class {feature_class_name} updated successfully.")
    else:
        arcpy.CopyFeatures_management(merged_fc, feature_class_path)
        print(f"Feature class {feature_class_name} created successfully.")

    arcpy.Delete_management(merged_fc)
    for layer in temp_layers:
        arcpy.Delete_management(layer)

    print("Update process completed.")
