'''
 Copyright (c) 2014, UChicago Argonne, LLC
 See LICENSE file.
'''

import PyQt4.QtGui as qtGui
import PyQt4.QtCore as qtCore
 
from rsMap3D.datasource.Sector33SpecDataSource import Sector33SpecDataSource
from rsMap3D.datasource.Sector33SpecDataSource import LoadCanceledException
from rsMap3D.gui.scanform import ScanForm
from rsMap3D.gui.fileform import FileForm
from rsMap3D.gui.datarange import DataRange
from rsMap3D.gui.dataextentview import DataExtentView
from rsMap3D.gui.processscans import ProcessScans
from rsMap3D.transforms.unitytransform3d import UnityTransform3D
from rsMap3D.transforms.polemaptransform3d import PoleMapTransform3D

import sys
import traceback
from rsMap3D.mappers.abstractmapper import ProcessCanceledException
from rsMap3D.exception.rsmap3dexception import ScanDataMissingException,\
    DetectorConfigException, InstConfigException, Transform3DException,\
    RSMap3DException
from rsMap3D.gui.qtsignalstrings import CURRENT_TAB_CHANGED
from rsMap3D.gui.rsmap3dsignals import LOAD_FILE_SIGNAL, CANCEL_LOAD_FILE_SIGNAL,\
    DONE_LOADING_SIGNAL, RANGE_CHANGED_SIGNAL, PROCESS_SIGNAL,\
    CANCEL_PROCESS_SIGNAL, FILE_ERROR_SIGNAL, PROCESS_ERROR_SIGNAL,\
    BLOCK_TABS_FOR_LOAD_SIGNAL, UNBLOCK_TABS_FOR_LOAD_SIGNAL,\
    BLOCK_TABS_FOR_PROCESS_SIGNAL, UNBLOCK_TABS_FOR_PROCESS_SIGNAL,\
    SET_PROCESS_RUN_OK_SIGNAL, SET_SCAN_LOAD_OK_SIGNAL,\
    SET_PROCESS_CANCEL_OK_SIGNAL, SET_SCAN_LOAD_CANCEL_SIGNAL,\
    LOAD_DATASOURCE_TO_SCAN_FORM_SIGNAL, SHOW_RANGE_BOUNDS_SIGNAL,\
    CLEAR_RENDER_WINDOW_SIGNAL, RENDER_BOUNDS_SIGNAL

class MainDialog(qtGui.QMainWindow):
    '''
    Main dialog for rsMap3D.  This class also serves as the over action 
    controller for the application
    '''
    def __init__(self,parent=None):
        '''
        '''
        super(MainDialog, self).__init__(parent)
        #Create and layout the widgets
        self.tabs = qtGui.QTabWidget()
        self.fileForm =FileForm()
        self.scanForm = ScanForm()
        self.dataRange = DataRange()
        self.processScans = ProcessScans()
        self.dataExtentView = DataExtentView()
        self.fileTabIndex = self.tabs.addTab(self.fileForm, "File")
        self.dataTabIndex = self.tabs.addTab(self.dataRange, "Data Range")
        self.scanTabIndex = self.tabs.addTab(self.scanForm, "Scans")
        self.processTabIndex = self.tabs.addTab(self.processScans, 
                                                "Process Data")
        self.tabs.setTabEnabled(self.dataTabIndex, False)
        self.tabs.setTabEnabled(self.scanTabIndex, False)
        self.tabs.setTabEnabled(self.processTabIndex, False)
        self.tabs.show()
        self.setCentralWidget(self.tabs)

        #Connect signals
        self.connect(self.fileForm, \
                     qtCore.SIGNAL(LOAD_FILE_SIGNAL), \
                     self.spawnLoadThread)
        self.connect(self.fileForm, \
                     qtCore.SIGNAL(CANCEL_LOAD_FILE_SIGNAL), \
                     self.cancelLoadThread)
        self.connect(self.scanForm, \
                     qtCore.SIGNAL(DONE_LOADING_SIGNAL), \
                     self.setupRanges)
        self.connect(self.dataRange, \
                     qtCore.SIGNAL(RANGE_CHANGED_SIGNAL), \
                     self.setScanRanges)
        self.connect(self.tabs, \
                     qtCore.SIGNAL(CURRENT_TAB_CHANGED), 
                     self.tabChanged)
        self.connect(self.processScans, \
                     qtCore.SIGNAL(PROCESS_SIGNAL), \
                     self.spawnProcessThread)
        self.connect(self.processScans, \
                     qtCore.SIGNAL(CANCEL_PROCESS_SIGNAL), \
                     self.stopMapper)
        self.connect(self, \
                     qtCore.SIGNAL(FILE_ERROR_SIGNAL), \
                     self.showFileError)
        self.connect(self, \
                     qtCore.SIGNAL(PROCESS_ERROR_SIGNAL), \
                     self.showProcessError)
        self.connect(self.processScans, \
                     qtCore.SIGNAL(PROCESS_ERROR_SIGNAL), \
                     self.showProcessError)
        
        self.connect(self, \
                     qtCore.SIGNAL(BLOCK_TABS_FOR_LOAD_SIGNAL), \
                     self.blockTabsForLoad)
        self.connect(self, \
                     qtCore.SIGNAL(UNBLOCK_TABS_FOR_LOAD_SIGNAL), \
                     self.unblockTabsForLoad)
        self.connect(self, \
                     qtCore.SIGNAL(BLOCK_TABS_FOR_PROCESS_SIGNAL), \
                     self.blockTabsForProcess)
        self.connect(self, \
                     qtCore.SIGNAL(UNBLOCK_TABS_FOR_PROCESS_SIGNAL), \
                     self.unblockTabsForProcess)
        self.connect(self, \
                     qtCore.SIGNAL(SET_PROCESS_RUN_OK_SIGNAL), \
                     self.processScans.setRunOK)
        self.connect(self, \
                     qtCore.SIGNAL(SET_PROCESS_CANCEL_OK_SIGNAL), \
                     self.processScans.setCancelOK)
        self.connect(self, \
                     qtCore.SIGNAL(SET_SCAN_LOAD_OK_SIGNAL), \
                     self.fileForm.setLoadOK)
        self.connect(self, \
                     qtCore.SIGNAL(SET_SCAN_LOAD_CANCEL_SIGNAL), \
                     self.fileForm.setCancelOK)
        self.connect(self, \
                     qtCore.SIGNAL(LOAD_DATASOURCE_TO_SCAN_FORM_SIGNAL), \
                     self.loadDataSourceToScanForm)
        self.connect(self.scanForm, \
                     qtCore.SIGNAL(SHOW_RANGE_BOUNDS_SIGNAL),
                     self.dataExtentView.showRangeBounds)
        self.connect(self.scanForm, \
                     qtCore.SIGNAL(CLEAR_RENDER_WINDOW_SIGNAL),
                     self.dataExtentView.clearRenderWindow)
        self.connect(self.scanForm, \
                     qtCore.SIGNAL(RENDER_BOUNDS_SIGNAL),
                     self.dataExtentView.renderBounds)
        
    def blockTabsForLoad(self):
        '''
        Disable tabs while loading
        '''
        self.tabs.setTabEnabled(self.dataTabIndex, False)
        self.tabs.setTabEnabled(self.scanTabIndex, False)
        self.tabs.setTabEnabled(self.processTabIndex, False)
        
    def blockTabsForProcess(self):
        '''
        disable tabs while processing
        '''
        self.tabs.setTabEnabled(self.dataTabIndex, False)
        self.tabs.setTabEnabled(self.scanTabIndex, False)
        self.tabs.setTabEnabled(self.fileTabIndex, False)
        
        
    def cancelLoadThread(self):
        '''
        Let the data source know that a cancel has been requested.
        '''
        self.dataSource.signalCancelLoadSource()
        
        
    def closeEvent(self, event):
        self.dataExtentView.vtkMain.close()
        
    def loadDataSourceToScanForm(self):
        '''
        '''
        self.scanForm.loadScanFile(self.dataSource)        
        
    def loadScanFile(self):
        '''
        Set up to load the scan file
        '''
        self.emit(qtCore.SIGNAL(BLOCK_TABS_FOR_LOAD_SIGNAL))
        if self.fileForm.getOutputType() == self.fileForm.SIMPLE_GRID_MAP_STR:
            self.transform = UnityTransform3D()
        elif self.fileForm.getOutputType() == self.fileForm.POLE_MAP_STR:
            self.transform = \
                PoleMapTransform3D(projectionDirection=\
                                   self.fileForm.getProjectionDirection())
        else:
            self.transform = None
            
             
        try:
            self.dataSource = \
                Sector33SpecDataSource(str(self.fileForm.getProjectDir()), \
                                       str(self.fileForm.getProjectName()), \
                                       str(self.fileForm.getProjectExtension()), \
                                       str(self.fileForm.getInstConfigName()), \
                                       str(self.fileForm.getDetConfigName()), \
                                       transform = self.transform, \
                                       scanList = self.fileForm.getScanList(), \
                                       roi = self.fileForm.getDetectorROI(), \
                                       pixelsToAverage = \
                                          self.fileForm.getPixelsToAverage(), \
                                       badPixelFile = \
                                          self.fileForm.getBadPixelFileName(), \
                                       flatFieldFile = \
                                          self.fileForm.getFlatFieldFileName() \
                                      )
            self.dataSource.setProgressUpdater(self.fileForm.updateProgress)
            self.dataSource.loadSource(mapHKL = self.fileForm.getMapAsHKL())
        except LoadCanceledException as e:
            print "LoadCanceled"
            self.emit(qtCore.SIGNAL(BLOCK_TABS_FOR_LOAD_SIGNAL))
            self.emit(qtCore.SIGNAL(SET_SCAN_LOAD_OK_SIGNAL))
            #self.fileForm.setLoadOK()
            return
        except ScanDataMissingException as e:
            self.emit(qtCore.SIGNAL(FILE_ERROR_SIGNAL), str(e))
            return
        except DetectorConfigException as e:
            self.emit(qtCore.SIGNAL(FILE_ERROR_SIGNAL), str(e))
            return
        except InstConfigException as e:
            self.emit(qtCore.SIGNAL(FILE_ERROR_SIGNAL), str(e))
            return
        except Transform3DException as e:
            self.emit(qtCore.SIGNAL(FILE_ERROR_SIGNAL), str(e))
            return 
        except ScanDataMissingException as e:
            self.emit(qtCore.SIGNAL(FILE_ERROR_SIGNAL), str(e))
            return
        except Exception as e:
            self.emit(qtCore.SIGNAL(FILE_ERROR_SIGNAL), str(e))
            print traceback.format_exc()
            return
        
            
        self.emit(qtCore.SIGNAL(LOAD_DATASOURCE_TO_SCAN_FORM_SIGNAL))
        self.emit(qtCore.SIGNAL(SET_SCAN_LOAD_OK_SIGNAL))
        
    def spawnLoadThread(self):
        '''
        Spawn a new thread to load the scan so that scan may be canceled later 
        and so that this does not interfere with the GUI operation.
        '''
        self.fileForm.setCancelOK()
        self.loadThread = LoadScanThread(self, parent=None)
        self.loadThread.start()
        
    def spawnProcessThread(self):
        '''
        Spawn a new thread to load the scan so that scan may be canceled later 
        and so that this does not interfere with the GUI operation.
        '''
        self.processScans.setProgressLimits(1, 
                                len(self.dataSource.getAvailableScans()))
        self.processScans.setCancelOK()
        self.processThread = ProcessScanThread(self, parent=None)
        self.processThread.start()
        
    def setupRanges(self):
        '''
        Get the overall data extent from the data source and set these values
        in the dataRange tab.  
        '''
        overallXmin, overallXmax, overallYmin, overallYmax, \
               overallZmin, overallZmax = self.dataSource.getOverallRanges()
        self.dataRange.setRanges(overallXmin, \
                                 overallXmax, \
                                 overallYmin, \
                                 overallYmax, \
                                 overallZmin, \
                                 overallZmax)
        self.setScanRanges()
        self.emit(qtCore.SIGNAL(UNBLOCK_TABS_FOR_LOAD_SIGNAL))
        
    def setScanRanges(self):
        '''
        Get the data range from the dataRange tab and set the bounds in this 
        class.  Tell scanForm tab to render the Qs for all scans.
        '''
        ranges = self.dataRange.getRanges()
        self.dataSource.setRangeBounds(ranges)
        self.scanForm.renderOverallQs()

    def showFileError(self, error):
        '''
        Show any errors from file loading in a message dialog.  When done, 
        toggle Load and Cancel buttons in file tab to Load Active/Cancel 
        inactive
        '''
        message = qtGui.QMessageBox()
        message.warning(self, \
                            "Load Scan File Warning", \
                             str(error))
        self.fileForm.setLoadOK()
              
    def tabChanged(self, index):
        '''
        When changing to the data range tab, display all qs from all scans.
        '''
        if str(self.tabs.tabText(index)) == "Data Range":
            self.scanForm.renderOverallQs()
                                        
    def runMapper(self):
        '''
        Tell the processScans tab to launch the mapper.
        '''
        self.emit(qtCore.SIGNAL(BLOCK_TABS_FOR_PROCESS_SIGNAL))
        self.emit(qtCore.SIGNAL(SET_PROCESS_CANCEL_OK_SIGNAL))
        try:
            self.processScans.runMapper(self.dataSource, self.transform)
        except ProcessCanceledException:
            self.emit(qtCore.SIGNAL(UNBLOCK_TABS_FOR_PROCESS_SIGNAL))
        except RSMap3DException as e:
            self.emit(qtCore.SIGNAL(PROCESS_ERROR_SIGNAL), str(e))
            print traceback.format_exc()
            return
        except Exception as e:
            self.emit(qtCore.SIGNAL(PROCESS_ERROR_SIGNAL), str(e))
            print traceback.format_exc()
            return
        self.emit(qtCore.SIGNAL(SET_PROCESS_RUN_OK_SIGNAL))
        self.emit(qtCore.SIGNAL(UNBLOCK_TABS_FOR_PROCESS_SIGNAL))
        
    def showProcessError(self, error):
        '''
        Show any errors from file processing in a message dialog.  When done, 
        toggle Load and Cancel buttons in file tab to Load Active/Cancel 
        inactive
        '''
        message = qtGui.QMessageBox()
        message.warning(self, \
                            "Processing Scan File Warning", \
                             str(error))
        self.emit(qtCore.SIGNAL(SET_PROCESS_RUN_OK_SIGNAL))
              
    def stopMapper(self):
        '''
        Tell the processScans tab to stop the mapper.
        '''
        self.processScans.stopMapper()
        
    def unblockTabsForLoad(self):
        '''
        enable tabs when done loading
        '''
        self.tabs.setTabEnabled(self.dataTabIndex, True)
        self.tabs.setTabEnabled(self.scanTabIndex, True)
        self.tabs.setTabEnabled(self.processTabIndex, True)
        
    def unblockTabsForProcess(self):
        '''
        enable tabs when done processing
        '''
        self.tabs.setTabEnabled(self.dataTabIndex, True)
        self.tabs.setTabEnabled(self.scanTabIndex, True)
        self.tabs.setTabEnabled(self.fileTabIndex, True)
        
class LoadScanThread(qtCore.QThread):
    '''
    Small thread class to launch the scan loading process
    '''
    def __init__(self, controller, **kwargs):
        super(LoadScanThread, self).__init__( **kwargs)
        self.controller = controller
        
    def run(self):
        self.controller.loadScanFile()
        
class ProcessScanThread(qtCore.QThread):
    '''
    Small thread class to launch data processing
    '''
    def __init__(self, controller, **kwargs):
        super(ProcessScanThread, self).__init__( **kwargs)
        self.controller = controller

    def run(self):
        self.controller.runMapper()
        
app = qtGui.QApplication(sys.argv)
mainForm = MainDialog()
mainForm.show()

app.exec_()
