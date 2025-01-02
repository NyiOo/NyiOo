# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'E:\Programming\Python\UI\MapWidget.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets



class Ui_Map_Form(object):
    def setupUi(self, Map_Form):
        Map_Form.setObjectName("Map_Form")
        Map_Form.resize(661, 320)
        self.gridLayout = QtWidgets.QGridLayout(Map_Form)
        self.gridLayout.setObjectName("gridLayout")
        self.checkBox = QtWidgets.QCheckBox(Map_Form)
        self.checkBox.setObjectName("checkBox")
        self.gridLayout.addWidget(self.checkBox, 0, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.gridLayout.addItem(spacerItem, 1, 0, 1, 1)
        self.groupBox_2 = QtWidgets.QGroupBox(Map_Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy)
        self.groupBox_2.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.groupBox_2.setObjectName("groupBox_2")
        self.formLayout_3 = QtWidgets.QFormLayout(self.groupBox_2)
        self.formLayout_3.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout_3.setRowWrapPolicy(QtWidgets.QFormLayout.DontWrapRows)
        self.formLayout_3.setContentsMargins(9, 9, -1, -1)
        self.formLayout_3.setObjectName("formLayout_3")
        self.comboBox = QtWidgets.QComboBox(self.groupBox_2)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.formLayout_3.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.comboBox)
        self.label_5 = QtWidgets.QLabel(self.groupBox_2)
        self.label_5.setObjectName("label_5")
        self.formLayout_3.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.lineEditLat = QtWidgets.QLineEdit(self.groupBox_2)
        self.lineEditLat.setObjectName("lineEditLat")
        self.formLayout_3.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.lineEditLat)
        self.label_6 = QtWidgets.QLabel(self.groupBox_2)
        self.label_6.setObjectName("label_6")
        self.formLayout_3.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_6)
        self.lineEditLong = QtWidgets.QLineEdit(self.groupBox_2)
        self.lineEditLong.setObjectName("lineEditLong")
        self.formLayout_3.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.lineEditLong)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.btnEnter = QtWidgets.QPushButton(self.groupBox_2)
        self.btnEnter.setObjectName("btnEnter")
        self.horizontalLayout_3.addWidget(self.btnEnter)
        self.btnRemove = QtWidgets.QPushButton(self.groupBox_2)
        self.btnRemove.setObjectName("btnRemove")
        self.horizontalLayout_3.addWidget(self.btnRemove)
        self.formLayout_3.setLayout(4, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout_3)
        self.label = QtWidgets.QLabel(self.groupBox_2)
        self.label.setObjectName("label")
        self.formLayout_3.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label)
        self.lineEditName = QtWidgets.QLineEdit(self.groupBox_2)
        self.lineEditName.setObjectName("lineEditName")
        self.formLayout_3.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.lineEditName)
        self.gridLayout.addWidget(self.groupBox_2, 2, 0, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 59, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 3, 0, 1, 1)
        self.vLayoutMap = QtWidgets.QVBoxLayout()
        self.vLayoutMap.setObjectName("vLayoutMap")
        self.gridLayout.addLayout(self.vLayoutMap, 0, 1, 4, 1)

        self.retranslateUi(Map_Form)
        QtCore.QMetaObject.connectSlotsByName(Map_Form)

    def retranslateUi(self, Map_Form):
        _translate = QtCore.QCoreApplication.translate
        Map_Form.setWindowTitle(_translate("Map_Form", "Map"))
        self.checkBox.setText(_translate("Map_Form", "Enable Virtual Station"))
        self.groupBox_2.setTitle(_translate("Map_Form", "  Location "))
        self.comboBox.setItemText(0, _translate("Map_Form", "Station 1"))
        self.comboBox.setItemText(1, _translate("Map_Form", "Station 2"))
        self.comboBox.setItemText(2, _translate("Map_Form", "Station 3"))
        self.label_5.setText(_translate("Map_Form", "Latitude"))
        self.label_6.setText(_translate("Map_Form", "Longitude"))
        self.btnEnter.setText(_translate("Map_Form", "Enter"))
        self.btnRemove.setText(_translate("Map_Form", "Remove"))
        self.label.setText(_translate("Map_Form", "Name"))
 
from PyQt5.QtWidgets import QInputDialog, QMessageBox       
from Map.PlugIn import  PlugIn       
import sys

class MapWidget(QtWidgets.QWidget, Ui_Map_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        self.map = PlugIn()
        stackviewer = self.map.graphicViewer()

        self.vLayoutMap.addWidget(stackviewer)
        self.EnableVirtualStation()

        stackviewer.viewer.leftMouseButtonDoubleClicked.connect(self.ShowInputDialog)
        # stackviewer.viewer.leftMouseButtonPressed.connect(self.PrintXY)
        stackviewer.viewer.DFlineClicked.connect(self.DeleteDFLine)
        self.btnEnter.clicked.connect(self.SetStations)
        self.btnRemove.clicked.connect(self.DeleteEllipse)
        self.comboBox.currentIndexChanged.connect(self.IndexChanged)
        self.checkBox.stateChanged.connect(self.EnableVirtualStation)
        
    def IndexChanged(self,value):
        x,y,n = self.map.convertBackData(value+1)
        self.lineEditLat.setText(str(y))
        self.lineEditLong.setText(str(x))
        self.lineEditName.setText(n)

    def SetStations(self):

        lat = self.lineEditLat.text()
        lon = self.lineEditLong.text()
        txt = self.lineEditName.text()

        if lat != '' and lon != '' and txt != '':
            try:
                index = self.comboBox.currentIndex()
                self.map.setStation(lon, lat, index+1, txt)
            except ValueError:
                self.ShowMessageBox("Lat & Long should be number")
                self.ClearAllTextEdit()
                return
        else:
            self.ShowMessageBox("Please Fill the blank")


    def ShowInputDialog(self,circle):
        if circle.index != 0:
            degree, ok = QInputDialog.getText(self, "Enter Virtual Degree", "Degree")
            if ok and degree != '':
                deg = int(degree)
                if deg <= 360:
                    self.map.setAngle(int(degree), circle.index)
                else:
                    self.ShowMessageBox("Degree should not be greater than 360")


    def ShowMessageBox(self,str):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(str)
        msg.setWindowTitle("Information")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()


    def DeleteDFLine(self,Df):
        self.map.deleteDFLine(Df)


    def DeleteEllipse(self):
        index = self.comboBox.currentIndex()
        self.map.CurrentStation(index+1)
        self.ClearAllTextEdit()


    def ClearAllTextEdit(self):
        self.lineEditLat.clear()
        self.lineEditLong.clear()
        self.lineEditName.clear()

    def EnableVirtualStation(self):
        if self.checkBox.checkState():
            self.comboBox.setEnabled(True)
            self.lineEditLat.setEnabled(True)
            self.lineEditLong.setEnabled(True)
            self.lineEditName.setEnabled(True)
            self.btnEnter.setEnabled(True)
            self.btnRemove.setEnabled(True)
        else:
            self.comboBox.setEnabled(False)
            self.lineEditLat.setEnabled(False)
            self.lineEditLong.setEnabled(False)
            self.lineEditName.setEnabled(False)
            self.btnEnter.setEnabled(False)
            self.btnRemove.setEnabled(False)

    def PrintXY(self,x,y):
        print(x,y)
        print(self.map.dataset.width, self.map.dataset.height)
        
    def SetAngle(self,angle,index):
        self.map.setAngle(angle, index)
        

if __name__=="__main__":
    app = QtWidgets.QApplication(sys.argv)
    form = MapWidget()
    form.show()
    sys.exit(app.exec_())