# Water Protection Zones — Python Scripts for Spatial Analysis

Набор Python-скриптов для обработки и анализа пространственных данных водных объектов, водоохранных зон, прибрежных полос и объектов загрязнения.
Разработано в рамках проекта по подготовке пространственной базы данных для веб-карты  
**«Информационно-аналитическая система "Водоохранные зоны"» Республики Беларусь.**

A set of Python scripts for processing and analyzing spatial data on water bodies, water protection zones, coastal protection zones, and pollution sources.
Developed as part of a project to prepare a spatial database for the web map  
**"Information and Analytical System 'Water Protection Zones'" of the Republic of Belarus.**

## 📁 scripts/data_preparation

### `merge_shapefiles_to_gdb.py`
Merges multiple shapefiles into a single feature class within a file geodatabase. Adds a text field with an identifier extracted from the filename and updates geometries in the geodatabase based on changes or new data.

**Main features:**
- Automatic GDB creation (if missing)
- Merging and ID field generation
- Updates, additions, and deletions based on `SOATO`
- Memory-efficient in-memory processing

**Usage example:**

```python
update_geodatabase(
    workspace="path/to/shapefiles",
    output_gdb="path/to/output.gdb",
    feature_class_name="CoastalProtectionZones",
    geom_type="POLYGON",
    id_field_name="SOATO",
    id_field_length=4
)
