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
import csv
import numpy as np
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
        return 'landslides_statistical_index'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('landslides_statistical_index')

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
        return 'geo403'

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr("This algorithm generates a landslide risk map for a study area using the statistical index method. For more information look at https://github.com/schreifab/GEO403-landslide-modelling .")

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """
        
        
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
        
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                "waterbodies",
                self.tr('waterbodies'),
                None
            )
        )
        
        
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
        Process algorithm. 
        """
        
        #author: Fabian Schreiter
        
        #set working dir
        os.chdir(parameters["output"])
        
        # init some settings
        QgsApplication.setPrefixPath((parameters["output"]), True) 
        QgsApplication.initQgis()

        #creste 2 directories if not exists
        if not os.path.exists('si_value_data'):
            os.makedirs('si_value_data')
        
        if not os.path.exists('si_raster_addition'):
            os.makedirs('si_raster_addition')
        
        
        # Genereate a viewshed vector layer
        viewshed_raster = processing.run("gdal:rastercalculator", {'INPUT_A':parameters["viewshed"],'BAND_A':1,'INPUT_B':None,'BAND_B':None,'INPUT_C':None,'BAND_C':None,'INPUT_D':None,'BAND_D':None,'INPUT_E':None,'BAND_E':None,'INPUT_F':None,'BAND_F':None,'FORMULA':'A >= 1','NO_DATA':None,'PROJWIN':None,'RTYPE':5,'OPTIONS':'','EXTRA':'','OUTPUT':'TEMPORARY_OUTPUT'})
        viewshed_polygons = processing.run("gdal:polygonize", {'INPUT':viewshed_raster['OUTPUT'],'BAND':1,'FIELD':'DN','EIGHT_CONNECTEDNESS':False,'EXTRA':'','OUTPUT':'TEMPORARY_OUTPUT'})
        
        viewshed_layer = QgsVectorLayer(viewshed_polygons['OUTPUT'])
        
        # remove all feauteres where DN = 0 (means not visisble)
        with edit(viewshed_layer):
            request = QgsFeatureRequest().setFilterExpression('"DN" = 0')
            request.setSubsetOfAttributes([])
            request.setFlags(QgsFeatureRequest.NoGeometry)

            # loop over the features and delete
            for f in viewshed_layer.getFeatures(request):
                viewshed_layer.deleteFeature(f.id())
        
        # sinngle to multi geom
        viewshed_multipolygon = processing.run("native:collect", {'INPUT':viewshed_layer,'FIELD':[],'OUTPUT':'viewshed.shp'})
        
        
        # generate an euclidian distance raster for roads
        roads_utm = processing.run("native:reprojectlayer", {'INPUT':parameters["roads"],'TARGET_CRS':QgsCoordinateReferenceSystem('EPSG:32648'),'OPERATION':'+proj=pipeline +step +proj=unitconvert +xy_in=deg +xy_out=rad +step +proj=utm +zone=48 +ellps=WGS84','OUTPUT':'TEMPORARY_OUTPUT'})
        roads_raster = processing.run("gdal:rasterize", {'INPUT':roads_utm['OUTPUT'],'FIELD':'','BURN':1,'USE_Z':False,'UNITS':1,'WIDTH':30,'HEIGHT':30,'EXTENT':None,'NODATA':0,'OPTIONS':'','DATA_TYPE':5,'INIT':None,'INVERT':False,'EXTRA':'','OUTPUT':'TEMPORARY_OUTPUT'})
        roads_distance = processing.run("gdal:proximity", {'INPUT':roads_raster['OUTPUT'],'BAND':1,'VALUES':'','UNITS':0,'MAX_DISTANCE':0,'REPLACE':0,'NODATA':0,'OPTIONS':'','EXTRA':'','DATA_TYPE':5,'OUTPUT':'TEMPORARY_OUTPUT'})

        dgm = parameters['dgm']
        
        # get extent and modify it for gdal
        raster_properties = processing.run("native:rasterlayerproperties", {'INPUT':dgm,'BAND':1})
        extent_from_qgis = raster_properties['EXTENT'].replace(' : ',',')
        extent_list = extent_from_qgis.split(',')
        extent_list[1],extent_list[2] = extent_list[2],extent_list[1]
        extent_4_gdal = ','.join(extent_list)
        extent = extent_4_gdal +' ['+raster_properties['CRS_AUTHID']+']'

        # clalculate slope, aspect, curvature, twi, spi from dgm
        slopeaspectcurvature = processing.run("saga:slopeaspectcurvature", {'ELEVATION':dgm,'SLOPE':'TEMPORARY_OUTPUT','ASPECT':'TEMPORARY_OUTPUT','C_GENE':'TEMPORARY_OUTPUT','C_PROF':'TEMPORARY_OUTPUT','C_PLAN':'TEMPORARY_OUTPUT','C_TANG':'TEMPORARY_OUTPUT','C_LONG':'TEMPORARY_OUTPUT','C_CROS':'TEMPORARY_OUTPUT','C_MINI':'TEMPORARY_OUTPUT','C_MAXI':'TEMPORARY_OUTPUT','C_TOTA':'TEMPORARY_OUTPUT','C_ROTO':'TEMPORARY_OUTPUT','METHOD':6,'UNIT_SLOPE':1,'UNIT_ASPECT':1})
        twi = processing.run("saga:topographicwetnessindextwi", {'SLOPE':slopeaspectcurvature['SLOPE'],'AREA':dgm,'TRANS':None,'TWI':'TEMPORARY_OUTPUT','CONV':0,'METHOD':0})
        spi = processing.run("saga:streampowerindex", {'SLOPE':slopeaspectcurvature['SLOPE'],'AREA':dgm,'SPI':'TEMPORARY_OUTPUT','CONV':0})
        
        #reclassification for unclassified rasters
        #reclassifictaion settings are found at the point table
        # '' means + or i infinity
        twi_classified = processing.run("native:reclassifybytable", {'INPUT_RASTER':twi['TWI'],'RASTER_BAND':1,'TABLE':['','-7','0','-7','0','1','0','7','2','7','','3'],'NO_DATA':-9999,'RANGE_BOUNDARIES':0,'NODATA_FOR_MISSING':False,'DATA_TYPE':5,'OUTPUT':'TEMPORARY_OUTPUT'})
        spi_classified = processing.run("native:reclassifybytable", {'INPUT_RASTER':spi['SPI'],'RASTER_BAND':1,'TABLE':['','250','0','250','500','1','500','750','2','750','1000','3','1000','','4'],'NO_DATA':-9999,'RANGE_BOUNDARIES':0,'NODATA_FOR_MISSING':False,'DATA_TYPE':5,'OUTPUT':'TEMPORARY_OUTPUT'})
        slope_classified = processing.run("native:reclassifybytable", {'INPUT_RASTER':slopeaspectcurvature['SLOPE'],'RASTER_BAND':1,'TABLE':['','10','0','10','20','1','20','30','2','30','40','3','40','50','4','50','','6'],'NO_DATA':-9999,'RANGE_BOUNDARIES':0,'NODATA_FOR_MISSING':False,'DATA_TYPE':5,'OUTPUT':'TEMPORARY_OUTPUT'})
        aspect_classified = processing.run("native:reclassifybytable", {'INPUT_RASTER':slopeaspectcurvature['ASPECT'],'RASTER_BAND':1,'TABLE':['0','45','0','45','90','1','90','135','2','135','180','3','180','225','4','225','270','5','270','315','6','315','360','7'],'NO_DATA':-9999,'RANGE_BOUNDARIES':0,'NODATA_FOR_MISSING':False,'DATA_TYPE':5,'OUTPUT':'TEMPORARY_OUTPUT'})
        c_plan_classified = processing.run("native:reclassifybytable", {'INPUT_RASTER':slopeaspectcurvature['C_PLAN'],'RASTER_BAND':1,'TABLE':['','0','0','0','','1'],'NO_DATA':-9999,'RANGE_BOUNDARIES':0,'NODATA_FOR_MISSING':False,'DATA_TYPE':5,'OUTPUT':'TEMPORARY_OUTPUT'})
        c_prof_classified = processing.run("native:reclassifybytable", {'INPUT_RASTER':slopeaspectcurvature['C_PROF'],'RASTER_BAND':1,'TABLE':['','0','0','0','','1'],'NO_DATA':-9999,'RANGE_BOUNDARIES':0,'NODATA_FOR_MISSING':False,'DATA_TYPE':5,'OUTPUT':'TEMPORARY_OUTPUT'})
        roads_classified = processing.run("native:reclassifybytable", {'INPUT_RASTER':roads_distance['OUTPUT'],'RASTER_BAND':1,'TABLE':['','30','0','30','60','1','60','90','2','90','','3'],'NO_DATA':-9999,'RANGE_BOUNDARIES':0,'NODATA_FOR_MISSING':False,'DATA_TYPE':5,'OUTPUT':'TEMPORARY_OUTPUT'})
        dgm_classified = processing.run("native:reclassifybytable", {'INPUT_RASTER':dgm,'RASTER_BAND':1,'TABLE':['','500','0','500','1000','1','1000','1500','2','1500','2000','3','2000','','4'],'NO_DATA':-9999,'RANGE_BOUNDARIES':0,'NODATA_FOR_MISSING':False,'DATA_TYPE':5,'OUTPUT':'TEMPORARY_OUTPUT'})
        
        
        # put all rasters in a list and name them in asecond list
        raster_clip_list = [dgm_classified['OUTPUT'],parameters['precipation'],parameters['soil'],parameters['landuse'],parameters['lithosphere'],parameters['waterbodies'],roads_classified['OUTPUT'],twi_classified['OUTPUT'],spi_classified['OUTPUT'],slope_classified['OUTPUT'],aspect_classified['OUTPUT'],c_plan_classified['OUTPUT'],c_prof_classified['OUTPUT']]
        raster_names = ['dgm','precip','soil','landuse','lithosphere','waterbodies','roads','twi','spi','slope','aspect','plan_curvature','profile_curvature']
        viewshed_raster_list = []
        
        i = 0
        #unique values (parameter classes) and clip all rasters to viewshed 
        for raster in raster_clip_list:
            processing.run("native:rasterlayeruniquevaluesreport", {'INPUT':raster,'BAND':1,'OUTPUT_HTML_FILE':'TEMPORARY_OUTPUT','OUTPUT_TABLE':raster_names[i]+'_unique_values.csv'})
            clip_result = processing.run("gdal:cliprasterbymasklayer", {'INPUT':raster,'MASK':viewshed_multipolygon['OUTPUT'],'SOURCE_CRS':None,'TARGET_CRS':None,'TARGET_EXTENT':None,'NODATA':None,'ALPHA_BAND':False,'CROP_TO_CUTLINE':True,'KEEP_RESOLUTION':False,'SET_RESOLUTION':False,'X_RESOLUTION':None,'Y_RESOLUTION':None,'MULTITHREADING':False,'OPTIONS':'','DATA_TYPE':0,'EXTRA':'','OUTPUT':'TEMPORARY_OUTPUT'})
            viewshed_raster_list.append(clip_result['OUTPUT'])
            i += 1
        
        # Zonal statistics for landslide raster on itsself to get the total amount of landslide pixels
        processing.run("native:rasterlayerzonalstats", {'INPUT':parameters['landslides'],'BAND':1,'ZONES':parameters['landslides'],'ZONES_BAND':1,'REF_LAYER':0,'OUTPUT_TABLE':'landslides_pixel.csv'})
        pixel_landslide_count = zonal_statistics_as_dic_from_csv('landslides_pixel.csv').get('1')
        
        i = 0
        statistical_index_raster_list = []
        
        # loop throgh every raster clipped by viewshed
        for raster in viewshed_raster_list:
            # Do Zonal statistics for every raster with the landslides and with itsself to get landlide pixel and total pixel for each parameter class
            processing.run("native:rasterlayerzonalstats", {'INPUT':parameters['landslides'],'BAND':1,'ZONES':raster,'ZONES_BAND':1,'REF_LAYER':0,'OUTPUT_TABLE': raster_names[i]+'_zonal.csv'})
            processing.run("native:rasterlayerzonalstats", {'INPUT':raster,'BAND':1,'ZONES':raster,'ZONES_BAND':1,'REF_LAYER':0,'OUTPUT_TABLE': raster_names[i]+'_class_pixel.csv'})
            pixel_zonal = zonal_statistics_as_dic_from_csv(raster_names[i]+'_zonal.csv')
            class_values = zonal_statistics_as_dic_from_csv(raster_names[i]+'_class_pixel.csv')
            unique_values = unique_values_from_csv(raster_names[i]+'_unique_values.csv')
            # create table for reclassification of the raster. Original class values will be replaced by statistical index values later
            reclass_table = create_statistical_index_list(pixel_zonal,class_values,pixel_landslide_count,unique_values)
            
            # write si values to file
            # write first and third value of every reclass table row because of the structure [min,max,value,min,max,value,min...]
            with open (raster_names[i]+'_si.txt', 'w', encoding='utf8') as f:
                i2 = 0
                for value in reclass_table:
                    if (i2 % 3 == 0):
                        f.write(value + ': ')
                    elif (i2 % 3 == 2):
                        f.write(value + ', ')
                    i2 += 1 

            # do reclassification
            si_raster = processing.run("native:reclassifybytable", {'INPUT_RASTER':raster_clip_list[i],'RASTER_BAND':1,'TABLE':reclass_table,'NO_DATA':-9999,'RANGE_BOUNDARIES':2,'NODATA_FOR_MISSING':False,'DATA_TYPE':5,'OUTPUT':'TEMPORARY_OUTPUT'})
            
            # warp every raster to project extent to avoid problems with the raster calculator
            si_raster_warped = processing.run("gdal:warpreproject", {'INPUT':si_raster['OUTPUT'],'SOURCE_CRS':None,'TARGET_CRS':None,'RESAMPLING':0,'NODATA':None,'TARGET_RESOLUTION':None,'OPTIONS':'','DATA_TYPE':0,'TARGET_EXTENT':extent,'TARGET_EXTENT_CRS':None,'MULTITHREADING':False,'EXTRA':'','OUTPUT':'si_value_data/si_values_'+raster_names[i]+'.tif'})
            statistical_index_raster_list.append(si_raster_warped['OUTPUT'])
            i += 1
            
        

        i = 1
        si_sum_raster = statistical_index_raster_list[0]
        # addition of all rasters
        while (i <= len(statistical_index_raster_list)-1):
            si_sum_raster = processing.run("gdal:rastercalculator", {'INPUT_A':si_sum_raster,'BAND_A':1,'INPUT_B':statistical_index_raster_list[i],'BAND_B':None,'INPUT_C':None,'BAND_C':None,'INPUT_D':None,'BAND_D':None,'INPUT_E':None,'BAND_E':None,'INPUT_F':None,'BAND_F':None,'FORMULA':'A + B','NO_DATA':None,'PROJWIN':None,'RTYPE':5,'OPTIONS':'','EXTRA':'','OUTPUT':'si_raster_addition/landslides_risk_si_'+str(i)+'.tif'})['OUTPUT']            #if i >= 2:
                #os.remove('landlides_risk_si_'+str(i-1)+'.tif')
            i += 1
        
        # add the results as layer to QGIS
        result_layer = QgsRasterLayer(si_sum_raster,"landslide_risk_map")
        QgsProject.instance().addMapLayer(result_layer)
        
        # no retrun needed because all results are exported to output folder during execution.
        # Currently it is not supposed to use this script in a chain of other functions
        #However, if you would like to do so, you need to define the output here
        return{}
        
        

def unique_values_from_csv(file):
    '''
    Returns an array of the parameter classes for each raster
    '''
     with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        i = 0
        list = []
        for row in csv_reader:
            if i != 0:
                # str->float->int->str to remove decimal places
                list.append(str(int(float(row[0]))))
            i += 1
        return list

def zonal_statistics_as_dic_from_csv(file):
    '''
    reads the zonal statistics as dic from csv
    '''
    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        i = 0
        dic = {}
        for row in csv_reader:
            if i != 0:
                # str->float->int->str to remove decimal places
                dic.update({str(int(float(row[0]))): float(row[3])})
            i += 1
        return dic
        
def create_statistical_index_list(pixel_landslides_per_class,pixel_per_class,pixel_landslide_count,unique_values):
    '''
    calculates the statistical index values and returns them in the structure of a qgis reclassification table
    '''
    list = []
    for key in unique_values:
        # for every class in raster
        if key in pixel_landslides_per_class:
            # if landlides in class
            list.append(key)
            list.append(key)
            # si value
            si = np.log((pixel_landslides_per_class.get(key)/pixel_per_class.get(key))/(pixel_landslide_count/sum(pixel_per_class.values())))
            list.append(str(si))
        else: 
            if key in pixel_per_class:
                # no landslides in class 
                list.append(key)
                list.append(key)
                # set landlides pixel from 0 to 0.1 because ln(0) is undefined (minus infinity)
                si = np.log((0.1/pixel_per_class.get(key))/(pixel_landslide_count/sum(pixel_per_class.values())))
                list.append(str(si))
            else: 
                # class does not appear in viewshed so its not considered for calculation. si -> 0
                list.append(key)
                list.append(key)
                si = 0
                list.append(str(si))
    return list
    
    

    