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
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFolderDestination,
                       QgsProcessingParameterNumber,
                       QgsApplication)
from qgis import processing
import os
import csv

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
        return 'roc'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Landuse ROC')

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
        return 'GEO403'

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr("This algorithm calculates the ROC for a landslide risk map. For more information look at https://github.com/schreifab/GEO403-landslide-modelling .")


    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                "riskmap",
                self.tr('risk map'),
                None
            )
        )
        
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                "landslides",
                self.tr('landslides'),
                None
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                "viewshed",
                self.tr('viewshed')
            )
        )
        
        self.addParameter(
            QgsProcessingParameterFolderDestination(
                "output",
                self.tr('Output folder')
            )
        )
        
        self.addParameter(
            QgsProcessingParameterNumber( 'i', 'Iterations', type=QgsProcessingParameterNumber.Integer)
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        #set working dir
        os.chdir(parameters["output"])
        
        # init some settings
        QgsApplication.setPrefixPath((parameters["output"]), True) 
        QgsApplication.initQgis()
        
        clip_raster = processing.run("gdal:cliprasterbymasklayer", {'INPUT':parameters['riskmap'],'MASK':parameters['viewshed'],'SOURCE_CRS':None,'TARGET_CRS':None,'TARGET_EXTENT':None,'NODATA':None,'ALPHA_BAND':False,'CROP_TO_CUTLINE':True,'KEEP_RESOLUTION':False,'SET_RESOLUTION':False,'X_RESOLUTION':None,'Y_RESOLUTION':None,'MULTITHREADING':False,'OPTIONS':'','DATA_TYPE':0,'EXTRA':'','OUTPUT':'raster_clipped.tif'})
        i = 0
        stats = processing.run("native:rasterlayerstatistics", {'INPUT':clip_raster['OUTPUT'],'BAND':1,'OUTPUT_HTML_FILE':'TEMPORARY_OUTPUT'})
        step_size = (stats['MAX'] - stats['MIN'])/ (float(parameters['i']) + 1)
        threshold = stats['MIN']
        #processing.run("native:rasterlayerzonalstats", {'INPUT':parameters['landslides'],'BAND':1,'ZONES':parameters['landslides'],'ZONES_BAND':1,'REF_LAYER':0,'OUTPUT_TABLE':'landslides_pixel.csv'})
        #pixel_landslide_count = zonal_statistics_as_dic_from_csv('landslides_pixel.csv').get('1')
        
        tpr = []
        fpr = []
        while i <= parameters['i'] - 1:
            threshold += step_size
            reclass_table = ['',str(threshold),'0',str(threshold),'','1']
            classified = processing.run("native:reclassifybytable", {'INPUT_RASTER':clip_raster['OUTPUT'],'RASTER_BAND':1,'TABLE':reclass_table,'NO_DATA':-9999,'RANGE_BOUNDARIES':0,'NODATA_FOR_MISSING':False,'DATA_TYPE':5,'OUTPUT':'TEMPORARY_OUTPUT'})
            processing.run("native:rasterlayerzonalstats", {'INPUT':parameters['landslides'],'BAND':1,'ZONES':classified['OUTPUT'],'ZONES_BAND':1,'REF_LAYER':0,'OUTPUT_TABLE': 'zonal'+str(i)+'.csv'})
            processing.run("native:rasterlayerzonalstats", {'INPUT':classified['OUTPUT'],'BAND':1,'ZONES':classified['OUTPUT'],'ZONES_BAND':1,'REF_LAYER':0,'OUTPUT_TABLE': 'class'+str(i)+'.csv'})
            pixel_zonal = zonal_statistics_as_dic_from_csv('zonal'+str(i)+'.csv')
            class_values = zonal_statistics_as_dic_from_csv('class'+str(i)+'.csv')
            if '1' in pixel_zonal:
                z1 = pixel_zonal.get('1')
            else: 
                z1 = 0
            if '0' in pixel_zonal:
                z0 = pixel_zonal.get('0')
            else: 
                z0 = 0
            
            tp = z1
            fn = z0
            tn = class_values.get('0') - z0
            fp = class_values.get('1') - z1
            tpr.append(tp/(tp+fn))
            fpr.append(fp/(fp+tn))
            
            i += 1
        
        i = 0
        with open ('roc.txt', 'w') as f:
            while i <= len(tpr) - 1:
                f.write(str(tpr[i])+','+str(fpr[i])+'\n')
                i += 1
            
        
        
        return {}
        
        
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
