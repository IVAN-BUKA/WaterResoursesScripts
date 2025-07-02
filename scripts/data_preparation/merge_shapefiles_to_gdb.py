import arcpy
import os

# === CONFIGURATION ===
input_folder = r"D:\WORK\CRICUWR\...\BELGIPROZEM_LAYERS_2024"  # Root folder containing subfolders with .shp files
output_gdb = r"D:\WORK\CRICUWR\...\MyProject1.gdb"             # Output geodatabase
feature_dataset_name = "HydroDataset"
merged_fc_name = "wo_giprozem_2024"

# === STEP 1. Search for all shapefiles in subfolders ===
shapefiles = [
    os.path.join(dirpath, file)
    for dirpath, _, files in os.walk(input_folder)
    for file in files if file.lower().endswith(".shp")
]

if not shapefiles:
    raise FileNotFoundError("No shapefiles found in the provided directory.")

print(f"Found {len(shapefiles)} shapefiles to merge.")

# === STEP 2. Use the spatial reference of the first shapefile ===
spatial_ref = arcpy.Describe(shapefiles[0]).spatialReference

# === STEP 3. Create GDB and Feature Dataset if they do not exist ===
if not arcpy.Exists(output_gdb):
    arcpy.CreateFileGDB_management(
        out_folder_path=os.path.dirname(output_gdb),
        out_name=os.path.basename(output_gdb)
    )
    print(f"Created File GDB: {output_gdb}")

feature_dataset_path = os.path.join(output_gdb, feature_dataset_name)

if not arcpy.Exists(feature_dataset_path):
    arcpy.CreateFeatureDataset_management(output_gdb, feature_dataset_name, spatial_ref)
    print(f"Created Feature Dataset: {feature_dataset_name}")

# === STEP 4. Merge shapefiles ===
merged_fc_path = os.path.join(feature_dataset_path, merged_fc_name)

# Copy the first shapefile
arcpy.CopyFeatures_management(shapefiles[0], merged_fc_path)

# Append the rest
if len(shapefiles) > 1:
    arcpy.Append_management(inputs=shapefiles[1:], target=merged_fc_path, schema_type="NO_TEST")

print(f"Merged {len(shapefiles)} shapefiles into: {merged_fc_path}")
