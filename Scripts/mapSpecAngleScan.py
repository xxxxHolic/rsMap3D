'''
 Copyright (c) 2017, UChicago Argonne, LLC
 See LICENSE file.
'''
'''
Script to process a dataset using the Sector33SpecDataSource
'''

import os
import numpy as np
import xrayutilities as xu
from rsMap3D.datasource.Sector33SpecDataSource import Sector33SpecDataSource
from rsMap3D.datasource.DetectorGeometryForXrayutilitiesReader import DetectorGeometryForXrayutilitiesReader as detReader
from rsMap3D.utils.srange import srange
from rsMap3D.config.rsmap3dconfigparser import RSMap3DConfigParser
from rsMap3D.constants import ENERGY_WAVELENGTH_CONVERT_FACTOR
from rsMap3D.mappers.gridmapper import QGridMapper
from rsMap3D.gui.rsm3dcommonstrings import BINARY_OUTPUT
from rsMap3D.transforms.unitytransform3d import UnityTransform3D
from rsMap3D.mappers.output.vtigridwriter import VTIGridWriter

def updateDataSourceProgress(value1, value2):
    print("DataSource Progress %s/%s" % (value1, value2))

def updateMapperProgress(value1):
    print("Mapper Progress %s" % (value1))


#
#Change values listed here for a particular experiment
#
roi = None    # defined later
projectDir = os.path.join("/Volumes/RSM_Data", "33data/Fe2O3_2")
specFile = "YSZ111_1.spc"

scanList1 = ['17-44',]
scanList2 = ['45-69',]

mapHKL = False

configDir = projectDir
detectorConfigName = os.path.join(configDir, "33bmDetectorGeometry.xml")
instConfigName = os.path.join(configDir, "33BM-instForXrayutilities.xml")
badPixelFile = os.path.join(configDir, "badpixels.txt")
if not os.path.exists(detectorConfigName):
    raise Exception("Detector Config file does not exist: %s" % 
                    detectorConfigName)
if not os.path.exists(instConfigName):
    raise Exception("Instrument Config file does not exist: %s" % 
                    instConfigName)
if not os.path.exists(badPixelFile):
    raise Exception("Bad Pixel file does not exist: %s" % 
                    badPixelFile)
    
dReader = detReader(detectorConfigName)

#detectorSettings
detectorName = "Pilatus"
# set to reduce data by averaging pixels 1,1 produces no averaging of pixels,
# uses the original data
bin = [1,1]
# Region of interesting
# set explicitly since the images are cropped by ROI
# COMMENT OUT roi or set to none to simply grab size from the calib file
roi = [1, 487, 1, 195]
# or get info from the config
if roi is None:
    detector = dReader.getDetectorById(detectorName)
    nPixels = dReader.getNpixels(detector)
    roi = [1, nPixels[0], 1, nPixels[1]]
print ("ROI: %s " % roi)

#output info = 
nx = 200
ny = 200
nz = 200
specName, specExt = os.path.splitext(specFile)
outputFileName = os.path.join(projectDir, specName + '.vti')
# note that the q ranges in the three dimensions are available
# later.  If you know resolution desired, it is possible to calculate more 
# appropriate nx, ny, nz

appConfig = RSMap3DConfigParser()
maxImageMemory = appConfig.getMaxImageMemory()

for scans in scanList1:
    scanRange = srange(scans).list()
    print ("scanRange %s" % scanRange)
    print("specName, specExt: %s, %s" % (specName, specExt))
    ds = Sector33SpecDataSource(projectDir, specName, specExt,
                                instConfigName, detectorConfigName, roi=roi, 
                                pixelsToAverage=bin, scanList= scanRange, 
                                badPixelFile=badPixelFile, 
                                appConfig=appConfig)
    ds.setCurrentDetector(detectorName)
    ds.setProgressUpdater(updateDataSourceProgress)
    ds.loadSource(mapHKL=mapHKL)
    ds.setRangeBounds(ds.getOverallRanges())
    imageToBeUsed = ds.getImageToBeUsed()
    print("imageToBeUsed %s" % imageToBeUsed)
#    wavelen = ENERGY_WAVELENGTH_CONVERT_FACTOR/ds.getIncidentEnergy()[scans[0]]
    imageSize = np.prod(ds.getDetectorDimensions())
    
    gridMapper = QGridMapper(ds,
                             outputFileName, 
                             outputType=BINARY_OUTPUT,
                             transform=UnityTransform3D(),
                             gridWriter=VTIGridWriter(),
                             appConfig=appConfig)

    gridMapper.setProgressUpdater(updateMapperProgress)
    gridMapper.doMap()
    
        