'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''
import os

from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QComboBox
from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QFileDialog
from PyQt4.QtGui import QGridLayout
from PyQt4.QtGui import QGroupBox
from PyQt4.QtGui import QIntValidator
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QMessageBox
from PyQt4.QtGui import QProgressBar
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QVBoxLayout

from rsMap3D.mappers.gridmapper import QGridMapper
from rsMap3D.mappers.polemapper import PoleFigureMapper

WARNING_STR = "Warning"

class ProcessScans(QDialog):
    '''
    This class presents a form to select to start analysis.  This display
    allows switching between Grid map and pole figure.
    '''
    POLE_MAP_STR = "Pole Map"
    GRID_MAP_STR = "Grid Map"
    
    def __init__(self, parent=None):
        '''
        Constructor - Layout widgets on the page & link up actions.
        '''
        super(ProcessScans, self).__init__(parent)
        self.Mapper = None
        layout = QVBoxLayout()

        self.dataBox = self._createDataBox()
        controlBox = self._createControlBox()
        

        layout.addWidget(self.dataBox)
        layout.addWidget(controlBox)
        self.setLayout(layout)                    
        
        
        
    def browseForOutputFile(self):
        '''
        Launch file browser to select the output file.  Checks are done to make
        sure the selected directory exists and that the selected file is 
        writable
        '''
        if self.outFileTxt.text() == "":
            fileName = str(QFileDialog.getSaveFileName(None, \
                                               "Save File", \
                                               filter="*.vti"))
        else:
            inFileName = str(self.outFileTxt.text())
            fileName = str(QFileDialog.getOpenFileName(None, 
                                               "Save File", 
                                               filter="*.vti", \
                                               directory = inFileName))
        if fileName != "":
            if os.path.exists(os.path.dirname(str(fileName))):
                self.outFileTxt.setText(fileName)
                self.outputFileName = fileName
                self.outFileTxt.emit(SIGNAL("editingFinished()"))
            else:
                message = QMessageBox()
                message.warning(self, \
                             WARNING_STR, \
                             "The specified directory does not exist")
                self.outFileTxt.setText(fileName)
                self.outputFileName = fileName
                self.outFileTxt.emit(SIGNAL("editingFinished()"))
            if not os.access(os.path.dirname(fileName), os.W_OK):
                message = QMessageBox()
                message.warning(self, \
                             WARNING_STR, \
                             "The specified fileis not writable")
            
    def cancelProcess(self):
        '''
        Emit a signal to trigger the cancelation of procesing.
        '''
        self.emit(SIGNAL("cancelProcess"))
        
    def _createControlBox(self):
        controlBox = QGroupBox()
        controlLayout = QGridLayout()
        row = 0
        self.progressBar = QProgressBar()
        controlLayout.addWidget(self.progressBar,row, 1)

        self.runButton = QPushButton("Run")
        controlLayout.addWidget(self.runButton, row, 3)

        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.setDisabled(True)

        controlLayout.addWidget(self.cancelButton, row, 4)

        self.connect(self.runButton, SIGNAL("clicked()"), self.process)
        self.connect(self.cancelButton, SIGNAL("clicked()"), self.cancelProcess)
        self.connect(self, SIGNAL("updateProgress"), 
                     self.setProgress)
        controlBox.setLayout(controlLayout)
        return controlBox
        
    def _createDataBox(self):
        '''
        Create Sub Layout for data gathering widgets
        '''
        dataBox = QGroupBox()
        dataLayout = QGridLayout()
        row = 0       
#        label = QLabel("Output Type")        
#        dataLayout.addWidget(label, row, 0)
        self.outTypeChooser = QComboBox()
        self.outTypeChooser.addItem(self.GRID_MAP_STR)
        self.outTypeChooser.addItem(self.POLE_MAP_STR)
#        dataLayout.addWidget(self.outTypeChooser, row,1)
#        row += 1

        label = QLabel("Grid Dimensions")
        dataLayout.addWidget(label, row,0)
        row += 1
        label = QLabel("X")
        dataLayout.addWidget(label, row,0)
        self.xDimTxt = QLineEdit()
        self.xDimTxt.setText("200")
        self.xDimValidator = QIntValidator()
        self.xDimTxt.setValidator(self.xDimValidator)
        dataLayout.addWidget(self.xDimTxt, row,1)
        
        row += 1
        label = QLabel("Y")
        dataLayout.addWidget(label, row,0)
        self.yDimTxt = QLineEdit()
        self.yDimTxt.setText("200")
        self.yDimValidator = QIntValidator()
        self.yDimTxt.setValidator(self.yDimValidator)
        dataLayout.addWidget(self.yDimTxt, row,1)
        
        row += 1
        label = QLabel("Z")
        dataLayout.addWidget(label, row,0)
        self.zDimTxt = QLineEdit()
        self.zDimTxt.setText("200")
        self.zDimValidator = QIntValidator()
        self.zDimTxt.setValidator(self.zDimValidator)
        dataLayout.addWidget(self.zDimTxt, row,1)
        
        row += 1
        label = QLabel("Output File")
        dataLayout.addWidget(label, row,0)
        self.outputFileName = ""
        self.outFileTxt = QLineEdit()
        self.outFileTxt.setText(self.outputFileName)
        dataLayout.addWidget(self.outFileTxt, row,1)
        self.outputFileButton = QPushButton("Browse")
        dataLayout.addWidget(self.outputFileButton, row, 2)

        self.connect(self.outputFileButton, SIGNAL("clicked()"), 
                     self.browseForOutputFile)
        self.connect(self.outputFileButton, SIGNAL("editFinished()"), 
                     self.editFinishedOutputFile)
        self.connect(self.outFileTxt, SIGNAL("editingFinished()"), \
                     self.editFinishedOutputFile)
        self.connect(self, SIGNAL("setFileName"), 
                     self.outFileTxt.setText)
        
        dataBox.setLayout(dataLayout)
        return dataBox
        
    def editFinishedOutputFile(self):
        '''
        When edititing is finished the a check is done to make sure that the 
        directory exists and the file is writable
        '''
        fileName = str(self.outFileTxt.text())
        if fileName != "":
            if os.path.exists(os.path.dirname(fileName)):
                #self.outFileTxt.setText(fileName)
                self.outputFileName = fileName
                #self.outFileTxt.emit(SIGNAL("editingFinished()"))
            else:
                if os.path.dirname(fileName) == "":
                    print("joining filename with current path")
                    curDir = os.path.realpath(os.path.curdir)
                    fileName = str(os.path.join(curDir, fileName))
                else:
                    message = QMessageBox()
                    message.warning(self, \
                                 WARNING_STR, \
                                 "The specified directory \n" + \
                                 str(os.path.dirname(fileName)) + \
                                 "\ndoes not exist")
                
#               self.outputFileName = fileName
                self.emit(SIGNAL("setFileName"), fileName)
                
            if not os.access(os.path.dirname(fileName), os.W_OK):
                message = QMessageBox()
                message.warning(self, \
                             WARNING_STR, \
                             "The specified fileis not writable")

    def process(self):
        '''
        Emit a signal to trigger the start of procesing.
        '''
        self.emit(SIGNAL("process"))
        
    def runMapper(self, dataSource, transform):
        '''
        Run the selected mapper
        '''
        self.dataSource = dataSource
        nx = int(self.xDimTxt.text())
        ny = int(self.yDimTxt.text())
        nz = int(self.zDimTxt.text())
        if self.outputFileName == "":
            self.outputFileName = os.path.join(dataSource.projectDir,  \
                                               "%s.vti" %dataSource.projectName)
            self.emit(SIGNAL("setFileName"), self.outputFileName)
        if os.access(os.path.dirname(self.outputFileName), os.W_OK):
            if (self.outTypeChooser.currentText() == self.GRID_MAP_STR):
                self.mapper = QGridMapper(dataSource, \
                                         self.outputFileName, \
                                         nx=nx, ny=ny, nz=nz,
                                         transform = transform)
                self.mapper.setProgressUpdater(self.updateProgress)
                self.mapper.doMap()
            else:
                self.mapper = PoleFigureMapper(dataSource, \
                                              self.outputFileName, \
                                              nx=nx, ny=ny, nz=nz, \
                                              transform = transform)
                self.mapper.doMap()
        else:
            self.emit(SIGNAL("processError"), \
                         "The specified directory \n" + \
                         str(os.path.dirname(self.outputFileName)) + \
                         "\nis not writable")

    def setCancelOK(self):
        '''
        If Cancel is OK the run button is disabled and the cancel button is 
        enabled
        '''
        self.runButton.setDisabled(True)
        self.cancelButton.setDisabled(False)
        self.dataBox.setDisabled(True)

    def setOutFileName(self, name):
        '''
        Write a filename to the text widget and to the stored output file name
        '''
        self.outFileTxt.setText(name)
        self.outputFileName = name
        
    def setProgress(self, value):
        '''
        Set the value in the progress bar
        '''
        self.progressBar.setValue(value)
        
    def setProgressLimits(self, min, max):
        '''
        Set the limits on the progress bar.
        '''
        self.progressBar.setMinimum(min)
        self.progressBar.setMaximum(max)
        
    def setRunOK(self):
        '''
        If Run is OK the load button is enabled and the cancel button is 
        disabled
        '''
        self.runButton.setDisabled(False)
        self.cancelButton.setDisabled(True)
        self.dataBox.setDisabled(False)
        
    def stopMapper(self):
        '''
        Halt the mapping process
        '''
        self.mapper.stopMap()
        
    def updateProgress(self, value):
        '''
        Send signal to update the progress bar.
        '''
        self.emit(SIGNAL("updateProgress"), value)
        