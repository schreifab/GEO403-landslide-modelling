# GEO403-landslide-modelling
This GitHub-Repository contains QGIS-proccessing scripts for the calculation of landslide risk in a study area. 
Therefore, the statistical index method and the weighting factor method can be used. 
![Flow chart](flow_chart.png)


## Requirements
The scripts can be executed via QGIS processing toolbox -> open existing script -> execute.
An Interface wil open.
Before running, the appropriate layers must be selected. 
IMPORTANT: Make sure that SAGA and GDAL are correctly installed in Your QGIS Version. Especially when using SAGA, problems can currently occur.
If so, uninstall and delete of all GQIS components and reinstall the latest QGIS version should solve the Problem. QGIS 3 is reqiured.

## Data 
Test data for a study area in Vietnam are given.
The data can be downloaded via http://leutra.geogr.uni-jena.de. The following Input Rasters are required:
dem: http://leutra.geogr.uni-jena.de/vgtbRBIS/metadata/view.php?view=geodata&id=887
lithosphere: http://leutra.geogr.uni-jena.de/vgtbRBIS/metadata/view.php?
soil: http://leutra.geogr.uni-jena.de/vgtbRBIS/metadata/view.php?
waterbodies: http://leutra.geogr.uni-jena.de/vgtbRBIS/metadata/view.php?view=geodata&id=1474
landuse: data-folder
roads: data-folder
viewshed: data-folder
precipation: data-folder

If you would like to use the algorithm for yur own study, make sure, that all rasters have the same EPSG and resolution. 

## Scripts

### landslides_si.py
This script calculates a landslide risk map using the statistical index method.

### landslides_wf.py
This script calculates a landslide risk map using the Weighting Factor method.
NOTE: There are no comments in the script, because it is just an adjusted Version of the one above. 
For detailed information take a look at landslides_si.py

### landslides_roc.py
This script can be used to validate the results. Therefore ROC is calculated. 
