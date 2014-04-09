'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''
import xml.etree.ElementTree as ET

NAMESPACE = '{https://subversion.xray.aps.anl.gov/RSM/instForXrayutils}'
#Element Names
DETECTOR_CIRCLES = NAMESPACE + 'detectorCircles'   
FILTER_NAME = NAMESPACE + 'filterName'   
INPLANE_REFERENCE_DIRECTION = NAMESPACE + 'inplaneReferenceDirection'   
MONITOR_NAME = NAMESPACE + 'monitorName'   
PRIMARY_ANGLE = NAMESPACE + 'primaryAngle'   
PRIMARY_BEAM_DIRECTION = NAMESPACE + 'primaryBeamDirection'
REFERENCE_ANGLE = NAMESPACE + 'referenceAngle'
SAMPLE_CIRCLES = NAMESPACE + 'sampleCircles'   
SAMPLE_SURFACE_NORMAL_DIRECTION = NAMESPACE + 'sampleSurfaceNormalDirection'   
SAMPLE_ANGLE_MAP_FUNCTION = NAMESPACE + 'sampleAngleMapFunction'   
#Attribute Names
AXIS_NUMBER = 'number'
DIRECTION_AXIS = 'directionAxis'
NAME = 'name'
NUM_CIRCLES = 'numCircles'
REFERENCE_AXIS = NAMESPACE + 'axis'
SCALE_FACTOR = 'scaleFactor'
SPEC_MOTOR_NAME = 'specMotorName'
CALC_ON_SCANNED_REF = 'calcOnScannedRef'

class InstForXrayutilitiesReader():
    '''
    '''

    def __init__(self, filename):
        '''
        '''
        self.root = None
        try:
            tree = ET.parse(filename)
        except IOError as ex:
            raise (IOError("Bad Instrument Configuration File" + str(ex)))
        self.root = tree.getroot()
        
    def getCircleAxisNumber(self, circle):
        '''
        '''
        return int(circle.attrib[AXIS_NUMBER])
        
    def getCircleDirection(self, circle):
        '''
        '''
        return circle.text
    
    def getDetectorCircleDirections(self):
        '''
        '''
        return self.makeCircleDirections(self.getDetectorCircles())
        
    def getCircleSpecMotorName(self, circle):
        '''
        '''
        return circle.attrib[SPEC_MOTOR_NAME]
    
    def getDetectorCircles(self):
        '''
        Return the detectpr childer as and element list.  If detector circles 
        is not included in the file raise an IOError
        '''
        circles = self.root.find(DETECTOR_CIRCLES)
        if circles == None:
            raise IOError("Instrument configuration has no Detector Circles")
        return self.root.find(DETECTOR_CIRCLES).getchildren()
        
    def getDetectorCircleNames(self):
        '''
        '''
        return self.makeCircleNames(self.getDetectorCircles())
        
    def getFilterName(self):
        '''
        Return the filterName if included in config file.  Returns None if it
        is not present. 
        '''
        name = self.root.find(FILTER_NAME)
        if name == None:
            return None
        else:
            return str(name.text)
    
    def getFilterScaleFactor(self):
        '''
        Return the scale factor to be used with filterName if included in 
        config file.  Returns 1 if it is not present. 
        '''
        name = self.root.find(FILTER_NAME)
        if name == None:
            return 1
        else:
            try:
                return float(name.attrib[SCALE_FACTOR])
            except KeyError:
                return 1
    
    def getInplaneReferenceDirection(self):
        '''
        '''
        direction = \
            self.root.find(INPLANE_REFERENCE_DIRECTION)
        return self.makeReferenceDirection(direction )
        
    def getMonitorName(self):
        '''
        Return the monitorName if included in config file.  Returns None if it
        is not present. 
        '''
        name = self.root.find(MONITOR_NAME)
        if name == None:
            return None
        else:
            return str(name.text)
    
    def getMonitorScaleFactor(self):
        '''
        Return the scale factor to be used with monitorName if included in 
        config file.  Returns 1 if it is not present. 
        '''
        name = self.root.find(MONITOR_NAME)
        if name == None:
            return 1
        else:
            try:
                return float(name.attrib[SCALE_FACTOR])
            except KeyError:
                return 1
    
    def getNumDetectorCircles(self):
        '''
        return the number of circles associated with the detector
        '''
        return int(self.root.find(DETECTOR_CIRCLES).attrib[NUM_CIRCLES])
    
    def getNumSampleCircles(self):
        '''
        return the number of circles associated with the sample
        '''
        return int(self.root.find(SAMPLE_CIRCLES).attrib[NUM_CIRCLES])
    
    def getPrimaryBeamDirection(self):
        '''
        '''
        direction = \
            self.root.find(PRIMARY_BEAM_DIRECTION)
        return self.makeReferenceDirection(direction )
        
    def getSampleAngleMappingCalcOnScannedRef(self):
        '''
        Returns true to run mapping function only when a reference angle is 
        scanned 
        '''
        function = self.root.find(SAMPLE_ANGLE_MAP_FUNCTION)
        if function == None:
            raise ValueError("No Mapping function defined in instrument " + \
                             "config file")
        if function.attrib[CALC_ON_SCANNED_REF] == None:
            return False
        else:
            if function.attrib[CALC_ON_SCANNED_REF].lower() in \
                ['true', '1', 'yes']:
                return True
            elif function.attrib[CALC_ON_SCANNED_REF].lower() in \
                ['false', '0', 'no']:
                return False
            else:
                raise ValueError("Error reading value for " + \
                                 "'calcOnScannedRef' from Instrument " + \
                                 "Config : " + \
                                 function.attrib[CALC_ON_SCANNED_REF])
                
                
    def getSampleAngleMappingFunctionName(self):
        '''
        Retrieve the name of a function to be used in mapping 
        '''
        function = self.root.find(SAMPLE_ANGLE_MAP_FUNCTION)
        if function == None:
            return ""
        else:
            return function.attrib[NAME]

    def getSampleAngleMappingPrimaryAngles(self):
        '''
        Retrieve the name of a function to be used in mapping 
        '''
        function = self.root.find(SAMPLE_ANGLE_MAP_FUNCTION)
        if function == None:
            raise ValueError("No Mapping function defined in instrument " + \
                             "config file")
        angles = []
        primaryAngles = function.findall(PRIMARY_ANGLE)
        if primaryAngles == None:
            raise ValueError("No primaryAngle members in " + \
            "sampleAngleMapFunction in instrument config")
        for angle in primaryAngles:
            angles.append(int(angle.attrib[AXIS_NUMBER]))
        return angles

    def getSampleAngleMappingReferenceAngles(self):
        '''
        Retrieve the name of a function to be used in mapping 
        '''
        function = self.root.find(SAMPLE_ANGLE_MAP_FUNCTION)
        if function == None:
            raise ValueError("No Mapping function defined in instrument " + \
                             "config file")
        angles = {}
        referenceAngles = function.findall(REFERENCE_ANGLE)
        if referenceAngles == None:
            raise ValueError("No referenceAngle members in " + \
            "sampleAngleMapFunction in instrument config")
        for angle in referenceAngles:
            angles[int(angle.attrib[AXIS_NUMBER])] = \
                angle.attrib[SPEC_MOTOR_NAME]
        return angles

    def getSampleCircleDirections(self):
        '''
        '''
        return self.makeCircleDirections(self.getSampleCircles())
        
    def getSampleCircles(self):
        '''
        Return the detectpr childer as and element list.  If detector circles 
        is not included in the file raise an IOError
        '''
        circles = self.root.find(SAMPLE_CIRCLES)
        if circles == None:
            raise IOError("Instrument configuration has no Sample Circles")
        return circles.getchildren()

    def getSampleCircleNames(self):
        '''
        '''
        return self.makeCircleNames(self.getSampleCircles())
        
    def getSampleSurfaceNormalDirection(self):
        '''
        '''
        direction = \
            self.root.find(SAMPLE_SURFACE_NORMAL_DIRECTION)
        return self.makeReferenceDirection(direction )
        
    def makeCircleDirections(self, circles):
        '''
        Create a list of circle directions from the XML
        '''
        data = []
        for circle in circles:
            data.append((int(circle.attrib[AXIS_NUMBER]), \
                            circle.attrib[SPEC_MOTOR_NAME], \
                            circle.attrib[DIRECTION_AXIS]))
        data.sort()
        directions = []
        for dataum in data:
            directions.append(dataum[2])
        return directions
    
    def makeCircleNames(self, circles):
        '''
        Create a list of circle names from the XML
        '''
        data = []
        for circle in circles:
            data.append((int(circle.attrib[AXIS_NUMBER]), \
                            circle.attrib[SPEC_MOTOR_NAME], \
                            circle.attrib[DIRECTION_AXIS]))
        data.sort()
        names = []
        for dataum in data:
            names.append(dataum[1])
        return names
    
    def makeReferenceDirection(self, direction):
        '''
        Create a list of reference directions from the XML
        '''
        axes = direction.findall(REFERENCE_AXIS)
        refAxis = {}
        for axis in axes:
            refAxis[int(axis.attrib[AXIS_NUMBER])] = int(axis.text)
        return [refAxis[1], refAxis[2], refAxis[3]]
    
        