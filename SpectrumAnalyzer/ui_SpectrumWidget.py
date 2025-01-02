# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'E:\Programming\SpectrumWidget.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Spectrum_Form(object):
    def setupUi(self, Spectrum_Form):
        Spectrum_Form.setObjectName("Spectrum_Form")
        Spectrum_Form.resize(472, 410)
        self.gridLayout = QtWidgets.QGridLayout(Spectrum_Form)
        self.gridLayout.setObjectName("gridLayout")
        self.spectrum_groupBox = QtWidgets.QGroupBox(Spectrum_Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.spectrum_groupBox.sizePolicy().hasHeightForWidth())
        self.spectrum_groupBox.setSizePolicy(sizePolicy)
        self.spectrum_groupBox.setMaximumSize(QtCore.QSize(16777215, 300))
        font = QtGui.QFont()
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.spectrum_groupBox.setFont(font)
        self.spectrum_groupBox.setObjectName("spectrum_groupBox")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.spectrum_groupBox)
        self.gridLayout_2.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.gridLayout_2.setSpacing(8)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label = QtWidgets.QLabel(self.spectrum_groupBox)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.spectrum_groupBox)
        self.label_3.setObjectName("label_3")
        self.gridLayout_2.addWidget(self.label_3, 2, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.spectrum_groupBox)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 1)
        self.pushButton_start = QtWidgets.QPushButton(self.spectrum_groupBox)
        self.pushButton_start.setObjectName("pushButton_start")
        self.gridLayout_2.addWidget(self.pushButton_start, 3, 1, 1, 1)
        self.pushButton_stop = QtWidgets.QPushButton(self.spectrum_groupBox)
        self.pushButton_stop.setObjectName("pushButton_stop")
        self.gridLayout_2.addWidget(self.pushButton_stop, 3, 2, 1, 1)
        self.startFreqSpinBox = QtWidgets.QDoubleSpinBox(self.spectrum_groupBox)
        self.startFreqSpinBox.setMinimumSize(QtCore.QSize(75, 0))
        self.startFreqSpinBox.setDecimals(3)
        self.startFreqSpinBox.setObjectName("startFreqSpinBox")
        self.gridLayout_2.addWidget(self.startFreqSpinBox, 0, 1, 1, 2)
        self.stopFreqSpinBox = QtWidgets.QDoubleSpinBox(self.spectrum_groupBox)
        self.stopFreqSpinBox.setDecimals(3)
        self.stopFreqSpinBox.setObjectName("stopFreqSpinBox")
        self.gridLayout_2.addWidget(self.stopFreqSpinBox, 1, 1, 1, 2)
        self.gainSpinBox = QtWidgets.QSpinBox(self.spectrum_groupBox)
        self.gainSpinBox.setObjectName("gainSpinBox")
        self.gridLayout_2.addWidget(self.gainSpinBox, 2, 1, 1, 2)
        self.gridLayout.addWidget(self.spectrum_groupBox, 1, 1, 1, 1)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.mainPlotLayout = GraphicsLayoutWidget(Spectrum_Form)
        self.mainPlotLayout.setObjectName("mainPlotLayout")
        self.verticalLayout.addWidget(self.mainPlotLayout)
        self.waterfallPlotLayout = GraphicsLayoutWidget(Spectrum_Form)
        self.waterfallPlotLayout.setObjectName("waterfallPlotLayout")
        self.verticalLayout.addWidget(self.waterfallPlotLayout)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 2, 1)
        spacerItem = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 0, 1, 1, 1)

        self.retranslateUi(Spectrum_Form)
        QtCore.QMetaObject.connectSlotsByName(Spectrum_Form)

    def retranslateUi(self, Spectrum_Form):
        _translate = QtCore.QCoreApplication.translate
        Spectrum_Form.setWindowTitle(_translate("Spectrum_Form", "Spectrum"))
        self.spectrum_groupBox.setTitle(_translate("Spectrum_Form", "  Frequency Control  "))
        self.label.setText(_translate("Spectrum_Form", "Start Freq (MHz) :"))
        self.label_3.setText(_translate("Spectrum_Form", "Gain (dB) :"))
        self.label_2.setText(_translate("Spectrum_Form", "Stop Freq (MHz) :"))
        self.pushButton_start.setText(_translate("Spectrum_Form", "Start"))
        self.pushButton_stop.setText(_translate("Spectrum_Form", "Stop"))

from pyqtgraph import GraphicsLayoutWidget
