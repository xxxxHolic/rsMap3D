'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''
from rsMap3D.exception.rsmap3dexception import DetectorConfigException
nameSpace = \
    '{https://subversion.xray.aps.anl.gov/RSM/detectorGeometryForXrayutils}'

import xml.etree.ElementTree as ET
import string

class DetectorGeometryForXrayutilitiesReader(object):
    '''
    This class is for reading detector geometry XML file for use with 
    xrayutilities
    :members:
    '''

    def __init__(self, filename):
        '''
        Constructor
        :param filename: name of the XML file holding the detector geomery
        '''
        self.DETECTORS = nameSpace + "Detectors"
        self.DETECTOR = nameSpace + "Detector"
        self.DETECTOR_ID = nameSpace + "ID"
        self.PIXEL_DIRECTION1 = nameSpace + 'pixelDirection1'
        self.PIXEL_DIRECTION2 = nameSpace + 'pixelDirection2'
        self.CENTER_CHANNEL_PIXEL = nameSpace + 'centerChannelPixel'
        self.NUMBER_OF_PIXELS = nameSpace + 'Npixels'
        self.DETECTOR_SIZE = nameSpace + 'size'
        self.DETECTOR_DISTANCE = nameSpace + 'distance'
        try:
            tree = ET.parse(filename)
        except IOError as ex:
            raise DetectorConfigException("Bad Detector Configuration File" + \
                                          str(ex))
        self.root = tree.getroot()
        
        
    def getCenterChannelPixel(self, detector):
        '''
        Return a list with two elements specifying the location of the center
        pixel
        :param detector: specifies the detector who's return value is requested
        :return: The location of the detector's center pixel 
        ''' 
        try:
            centerPix = detector.find(self.CENTER_CHANNEL_PIXEL).text
        except AttributeError:
            raise DetectorConfigException(self.CENTER_CHANNEL_PIXEL + 
                                          " not found in detector config " + \
                                          "file")
        vals = string.split(centerPix)
        return [int(vals[0]), int(vals[1])]
    
    def getDetectors(self):
        '''
        :return: a list of detectors in the configuration
        
        '''
        detectors = self.root.find(self.DETECTORS)
        if detectors == None:
            raise DetectorConfigException("No detectors found in detector " + \
                                          "config file")
        return detectors
    
    def getDetectorById(self, identifier):
        '''
        return a particular by specifying it's ID 
        :param identifier: the id of the specified detector 
        :return: The requested detector
        '''
        try:
            dets = self.getDetectors().findall(self.DETECTOR)
        except AttributeError:
            raise DetectorConfigException("No detectors found in detector " + \
                                          "config file")
        for detector in dets:
            detId = detector.find(self.DETECTOR_ID)
            if detId.text == identifier:
                return detector
        raise DetectorConfigException("Detector " + 
                                      identifier + 
                                      " not found in detector config file")

    def getDetectorID(self, detector):
        '''
        :param detector: specifies the detector who's return value is requested
        :return: The ID of the specified detector detector
        '''
        return detector.find(self.DETECTOR_ID).text

    def getDistance(self, detector):
        '''
        :param detector: specifies the detector who's return value is requested
        :return: The sample to detector distance
        '''
        return float(detector.find(self.DETECTOR_DISTANCE).text)
    
    def getNpixels(self, detector):
        '''
        :param detector: specifies the detector who's return value is requested
        :return: A list with two elements specifying the size of the detector
        in pixels
        ''' 
        vals = string.split(detector.find(self.NUMBER_OF_PIXELS).text)
        return [int(vals[0]), int(vals[1])]
    
    def getPixelDirection1(self, detector):
        '''
        :param detector: specifies the detector who's return value is requested
        :return: The direction for increasing the first pixel dimension (x+ 
        specifies the first dimension increases in the positive x direction)
        '''
        return detector.find(self.PIXEL_DIRECTION1).text

    def getPixelDirection2(self, detector):
        '''
        :param detector: specifies the detector who's return value is requested
        :return:  The direction for increasing the second pixel dimension (y- 
        specifies the second dimension increases in the negative y direction)
        '''
        return detector.find(self.PIXEL_DIRECTION2).text

    def getSize(self, detector):
        '''
        :param detector: specifies the detector who's return value is requested
        :return: The size of the detector in millimeters
        '''
        vals = string.split(detector.find(self.DETECTOR_SIZE).text)
        return [float(vals[0]), float(vals[1])]
    
