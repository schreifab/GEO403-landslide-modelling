# -*- coding: utf-8 -*-

"""
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterFolderDestination,
                       QgsProject,
                       QgsRasterLayer,
                       QgsVectorLayer,
                       QgsApplication,
                       QgsFeatureRequest,
                       QgsCoordinateReferenceSystem,
                       edit
                       )
from qgis import processing
from qgis.analysis import (QgsRasterCalculatorEntry, QgsRasterCalculator)
import os
#import QgsProject

class ExampleProcessingAlgorithm(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ExampleProcessingAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'landslide_1'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('landslide_1')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr('GEO403')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'examplescripts'

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr("Example algorithm short description")

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """
        #author: Fabian Schreiter
        
        #We add the input vector features source. It can have any kind of
        #geometry.
        
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                "landslides",
                self.tr('landslides'),
                None
            )
        )
        
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                "dgm",
                self.tr('dgm'),
                None
            )
        )
        
        
        
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                "viewshed",
                self.tr('viewshed'),
                None
            )
        )
        

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                "soil",
                self.tr('soil'),
                None
            )
        )
        
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                "lithosphere",
                self.tr('lithosphere'),
                None
            )
        )
        
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                "landuse",
                self.tr('landuse'),
                None
            )
        )
        
        # self.addParameter(
            # QgsProcessingParameterRasterLayer(
                # "waterbodies",
                # self.tr('waterbodies'),
                # None
            # )
        # )
        
        
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                "precipation",
                self.tr('precipation')
            )
        )
        
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                "roads",
                self.tr('roads')
            )
        )
        

        

        self.addParameter(
            QgsProcessingParameterFolderDestination(
                "output",
                self.tr('Output folder')
            )
        )
        


    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        #slope_file = "slope.tif"
        map_layers = QgsProject.instance().mapLayers()
        
        
        # entries = []
        
        # viewshed_layer = map_layers[(parameters["viewshed"])]
        # band = viewshed_layer.bandName(1)[8:]+'@1'
        # print(band)
        os.chdir(parameters["output"])
        QgsApplication.setPrefixPath((parameters["output"]), True) 
        QgsApplication.initQgis()
        # ras = QgsRasterCalculatorEntry()
        # ras.ref = band
        # ras.raster = viewshed_layer
        # ras.bandNumber = 1
        # entries.append(ras)
        # calc = QgsRasterCalculator(band + '>= 1', 'viewshed_new.tif', 'GTiff', viewshed_layer.extent(), viewshed_layer.width(), viewshed_layer.height(), entries)
        
        viewshed_raster = processing.run("gdal:rastercalculator", {'INPUT_A':parameters["viewshed"],'BAND_A':1,'INPUT_B':None,'BAND_B':None,'INPUT_C':None,'BAND_C':None,'INPUT_D':None,'BAND_D':None,'INPUT_E':None,'BAND_E':None,'INPUT_F':None,'BAND_F':None,'FORMULA':'A >= 1','NO_DATA':None,'PROJWIN':None,'RTYPE':5,'OPTIONS':'','EXTRA':'','OUTPUT':'TEMPORARY_OUTPUT'})
        viewshed_polygons = processing.run("gdal:polygonize", {'INPUT':viewshed_raster['OUTPUT'],'BAND':1,'FIELD':'DN','EIGHT_CONNECTEDNESS':False,'EXTRA':'','OUTPUT':'TEMPORARY_OUTPUT'})
        
        viewshed_layer = QgsVectorLayer(viewshed_polygons['OUTPUT'])
        with edit(viewshed_layer):
            # build a request to filter the features based on an attribute
            request = QgsFeatureRequest().setFilterExpression('"DN" = 0')


            request.setSubsetOfAttributes([])
            request.setFlags(QgsFeatureRequest.NoGeometry)

            # loop over the features and delete
            for f in viewshed_layer.getFeatures(request):
                viewshed_layer.deleteFeature(f.id())
        
        viewshed_multipolygon = processing.run("native:collect", {'INPUT':viewshed_layer,'FIELD':[],'OUTPUT':'viewshed.shp'})
        
        roads_utm = processing.run("native:reprojectlayer", {'INPUT':parameters["roads"],'TARGET_CRS':QgsCoordinateReferenceSystem('EPSG:32648'),'OPERATION':'+proj=pipeline +step +proj=unitconvert +xy_in=deg +xy_out=rad +step +proj=utm +zone=48 +ellps=WGS84','OUTPUT':'TEMPORARY_OUTPUT'})
        roads_raster = processing.run("gdal:rasterize", {'INPUT':roads_utm['OUTPUT'],'FIELD':'','BURN':1,'USE_Z':False,'UNITS':1,'WIDTH':30,'HEIGHT':30,'EXTENT':None,'NODATA':0,'OPTIONS':'','DATA_TYPE':5,'INIT':None,'INVERT':False,'EXTRA':'','OUTPUT':'TEMPORARY_OUTPUT'})
        roads_distance = processing.run("gdal:proximity", {'INPUT':roads_raster['OUTPUT'],'BAND':1,'VALUES':'','UNITS':1,'MAX_DISTANCE':0,'REPLACE':0,'NODATA':0,'OPTIONS':'','EXTRA':'','DATA_TYPE':5,'OUTPUT':'TEMPORARY_OUTPUT'})
        roads_distance = processing.run("gdal:proximity", {'INPUT':roads_raster['OUTPUT'],'BAND':1,'VALUES':'','UNITS':1,'MAX_DISTANCE':0,'REPLACE':0,'NODATA':0,'OPTIONS':'','EXTRA':'','DATA_TYPE':5,'OUTPUT':'TEMPORARY_OUTPUT'})
        
        dgm = parameters['dgm']
        slopeaspectcurvature = processing.run("saga:slopeaspectcurvature", {'ELEVATION':dgm,'SLOPE':'TEMPORARY_OUTPUT','ASPECT':'TEMPORARY_OUTPUT','C_GENE':'TEMPORARY_OUTPUT','C_PROF':'TEMPORARY_OUTPUT','C_PLAN':'TEMPORARY_OUTPUT','C_TANG':'TEMPORARY_OUTPUT','C_LONG':'TEMPORARY_OUTPUT','C_CROS':'TEMPORARY_OUTPUT','C_MINI':'TEMPORARY_OUTPUT','C_MAXI':'TEMPORARY_OUTPUT','C_TOTA':'TEMPORARY_OUTPUT','C_ROTO':'TEMPORARY_OUTPUT','METHOD':6,'UNIT_SLOPE':0,'UNIT_ASPECT':0})
        twi = processing.run("grass7:r.topidx", {'input':dgm,'output':'TEMPORARY_OUTPUT','GRASS_REGION_PARAMETER':None,'GRASS_REGION_CELLSIZE_PARAMETER':0,'GRASS_RASTER_FORMAT_OPT':'','GRASS_RASTER_FORMAT_META':''})

        
        #reclassification
        twi_classified = processing.run("native:reclassifybytable", {'INPUT_RASTER':twi['output'],'RASTER_BAND':1,'TABLE':['2','7','0','7','12','1','12','17','2','17','23','3'],'NO_DATA':-9999,'RANGE_BOUNDARIES':0,'NODATA_FOR_MISSING':False,'DATA_TYPE':5,'OUTPUT':'TEMPORARY_OUTPUT'})
        slope_classified = processing.run("native:reclassifybytable", {'INPUT_RASTER':slopeaspectcurvature['SLOPE'],'RASTER_BAND':1,'TABLE':['0','10','0','10','20','1','20','30','2','30','40','3','40','50','4','50','61','6'],'NO_DATA':-9999,'RANGE_BOUNDARIES':0,'NODATA_FOR_MISSING':False,'DATA_TYPE':5,'OUTPUT':'TEMPORARY_OUTPUT'})
        aspect_classified = processing.run("native:reclassifybytable", {'INPUT_RASTER':slopeaspectcurvature['ASPECT'],'RASTER_BAND':1,'TABLE':['0','45','0','45','90','1','90','135','2','135','180','3','180','225','4','225','270','5','270','315','6','315','360','7'],'NO_DATA':-9999,'RANGE_BOUNDARIES':0,'NODATA_FOR_MISSING':False,'DATA_TYPE':5,'OUTPUT':'TEMPORARY_OUTPUT'})
        c_plan_classified = processing.run("native:reclassifybytable", {'INPUT_RASTER':slopeaspectcurvature['C_PLAN'],'RASTER_BAND':1,'TABLE':['-20','0','0','0','135','1'],'NO_DATA':-9999,'RANGE_BOUNDARIES':0,'NODATA_FOR_MISSING':False,'DATA_TYPE':5,'OUTPUT':'TEMPORARY_OUTPUT'})
        c_prof_classified = processing.run("native:reclassifybytable", {'INPUT_RASTER':slopeaspectcurvature['C_PROF'],'RASTER_BAND':1,'TABLE':['-1','0','0','0','1','1'],'NO_DATA':-9999,'RANGE_BOUNDARIES':0,'NODATA_FOR_MISSING':False,'DATA_TYPE':5,'OUTPUT':'TEMPORARY_OUTPUT'})
        roads_classified = processing.run("native:reclassifybytable", {'INPUT_RASTER':roads_distance['OUTPUT'],'RASTER_BAND':1,'TABLE':['0','30','0','30','60','1','60','90','2','90','3000','3'],'NO_DATA':-9999,'RANGE_BOUNDARIES':0,'NODATA_FOR_MISSING':False,'DATA_TYPE':5,'OUTPUT':'TEMPORARY_OUTPUT'})
        dgm_classified = processing.run("native:reclassifybytable", {'INPUT_RASTER':dgm,'RASTER_BAND':1,'TABLE':['-1','500','0','500','1000','1','1000','1500','2','1500','2000','3','2000','2700','4'],'NO_DATA':-9999,'RANGE_BOUNDARIES':0,'NODATA_FOR_MISSING':False,'DATA_TYPE':5,'OUTPUT':'TEMPORARY_OUTPUT'})
        
        raster_clip_list = [dgm_classified['OUTPUT'],parameters['precipation'],parameters['soil'],parameters['landuse'],parameters['lithosphere'],roads_classified['OUTPUT'],twi_classified['OUTPUT'],slope_classified['OUTPUT'],aspect_classified['OUTPUT'],c_plan_classified['OUTPUT'],c_prof_classified['OUTPUT']]
        raster_names = ['dgm','precip','soil','landuse','lithosphere','roads','twi','slope','aspect','plan_curvature','profile_curvature']
        viewshed_raster_list = []
        
        #clip all rasters to viewshed
        for raster in raster_clip_list:
            clip_result = processing.run("gdal:cliprasterbymasklayer", {'INPUT':raster,'MASK':viewshed_multipolygon['OUTPUT'],'SOURCE_CRS':None,'TARGET_CRS':None,'TARGET_EXTENT':None,'NODATA':None,'ALPHA_BAND':False,'CROP_TO_CUTLINE':True,'KEEP_RESOLUTION':False,'SET_RESOLUTION':False,'X_RESOLUTION':None,'Y_RESOLUTION':None,'MULTITHREADING':False,'OPTIONS':'','DATA_TYPE':0,'EXTRA':'','OUTPUT':'TEMPORARY_OUTPUT'})
            viewshed_raster_list.append(clip_result['OUTPUT'])
            
        
        i = 0
        for raster in viewshed_raster_list:
            processing.run("native:rasterlayerzonalstats", {'INPUT':parameters['landslides'],'BAND':1,'ZONES':raster,'ZONES_BAND':1,'REF_LAYER':0,'OUTPUT_TABLE': raster_names[i]+'zonal.csv'})
            i += 1

        
        
        
        
        
       


        
        
        #result_slope = processing.run("gdal:slope",{'BAND': 1, 'INPUT': parameters["dgm"],'SCALE':1,'OUTPUT': 'TEMPORARY_OUTPUT'},
            #context=context, feedback=feedback, is_child_algorithm=True)
            
        
        
        
        #slope_layer = QgsRasterLayer(slope_file,"slope")
        #QgsProject.instance().addMapLayer(slope_layer)
        #print(slope_layer)
        #return {self.OUTPUT: result_slope}
        
        return{}
