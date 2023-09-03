from __main__ import vtk, qt, ctk, slicer
from DICOMLib import DICOMUtils
import csv
import os

class LoadDataFromFolder:
    def __init__(self, parent):
        parent.title = "Load Data from a folder"
        parent.categories = ["Custom"]
        parent.dependencies = []
        parent.contributors = ["Mattis Teschner"]
        parent.helpText = "Lade Daten in die Scene aus einem Input Folder"

        parent.acknowledgementText = "Ich danke der 3D Slicer Dokumentation"

        self.parent = parent

class LoadDataFromFolderWidget:
    def __init__(self, parent = None):
        if not parent:
            self.parent = slicer.qMRMLWidget()
            self.parent.setLayout(qt.QVBoxLayout())
            self.parent.setMRMLScene(slicer.mrmlScene)
        else:
            self.parent = parent
        self.layout = self.parent.layout()
        if not parent:
            self.setup()
            self.parent.show()

    def setup(self):
        #pathfield
        self.pathfield = qt.QLineEdit()
        self.pathfield.placeholderText = "shows the path of the selected folder"
        self.pathfield.readOnly = True

        #loadButton
        self.loadButton = qt.QPushButton("Load Data")
        self.loadButton.toolTip = "Lädt Daten aus einen Ordner in die Scene"
        self.loadButton.connect("clicked(bool)", self.importData)

        #selectButton 
        self.selectButton = qt.QPushButton("select new folder")
        self.selectButton.toolTip = "ermöglicht die Auswahl eines Ordners, dessen inhalt importiert werden soll"
        self.selectButton.connect("clicked(bool)", self.selectDir)

        #checkbutton
        self.checkButton = qt.QCheckBox("Load Data when starting Slicer (not working currently)")
        self.checkButton.stateChanged.connect(self.checkBoxPressed) #connecting the checkbox signal to the method

        self.layout.addWidget(self.selectButton)
        self.layout.addWidget(self.pathfield)
        self.layout.addWidget(self.loadButton)
        self.layout.addWidget(self.checkButton)

        #updating the pathfield
        try:
            self.pathfield.setText(self.readcsv(0))
        except:
            pass
        
        #updating the checkbutton and loading data out of the folder when the button was checked
        try:
            if self.readcsv(1) == "True":
                self.checkButton.setChecked(True)
                self.importData()

            else:
                self.checkButton.setChecked(False)

        except:
            pass

        #check whether the folder does exist
        if not os.path.exists(str(os.path.dirname(__file__))+"\\Data"):
            os.makedirs(str(os.path.dirname(__file__))+"\\Data")

    #import data out of a folder into the scene
    def importData(self):
        # nötige Variablen
        loadedNodeIDs = []

        dicomDataDir = self.pathfield.text # Get the current Directory Name out of the field

        with DICOMUtils.TemporaryDICOMDatabase() as db:
            DICOMUtils.importDicom(dicomDataDir, db)
            patientUIDs = db.patients()
            for patientUID in patientUIDs:
                loadedNodeIDs.extend(DICOMUtils.loadPatientByUID(patientUID))

    #Schreibt Daten auf ein Ziel-File
    def write2CSV(self, pos:int, new_data, placeholder=None):

        try:#file allready exists
            with open(str(os.path.dirname(__file__))+"\\Data\\LoadDataFromFolder.csv", mode="r", newline='') as csvfile:
            
                #Read the Data out of the csvFile into a list
                data = []
                csvReader = csv.reader(csvfile)
                for row in csvReader:
                    for column in row:
                        data.append(column)

                #append placeholders when nessesary
                if pos > len(data)-1:
                    for i in range(len(data)-1, pos):
                        data.append(placeholder)

                # changing the data
                data[pos] = new_data

        except:#file needs to be created
            data = []
            #expanding the list when nessesary
            if pos > len(data)-1:
                for i in range(0, pos+1):
                    data.append(placeholder)

            #adding the data
            data[pos] = new_data

        #writing the data onto th file
        with open(str(os.path.dirname(__file__))+"\\Data\\LoadDataFromFolder.csv", mode="w", newline='') as csvfile:
            csvWriter = csv.writer(csvfile)
            csvWriter.writerow(data)

    #read csv files
    def readcsv(self, pos):
        with open(str(os.path.dirname(__file__))+"\\Data\\LoadDataFromFolder.csv", mode="r", newline='') as csvfile:
            #Read the Data out of the csvFile into a list
            data = []
            csvReader = csv.reader(csvfile)
            for row in csvReader:
                for column in row:
                    data.append(column)

        return data[pos]

    #selection einer directory
    def selectDir(self):
        #getting the path of a directory
        path = qt.QFileDialog.getExistingDirectory()
        #einsetzen des Pfadees in das Textfeld
        self.pathfield.setText(path)
        #Der Pfad wird in der csv Datei gespeichert
        self.write2CSV(0, path)

    #is connected to the signal of the checkbutton
    def checkBoxPressed(self, state):
        if state == 2: #checked
            self.write2CSV(1, "True")
        elif state == 0: #unchecked
            self.write2CSV(1, "False")