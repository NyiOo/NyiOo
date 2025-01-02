# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'E:\Programming\DFWidget.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class DF_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("DF_Form")
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setFormAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft)
        self.formLayout.setContentsMargins(30, -1, 5, -1)
        self.formLayout.setHorizontalSpacing(20)
        self.formLayout.setVerticalSpacing(15)
        self.formLayout.setObjectName("formLayout")
        self.label_5 = QtWidgets.QLabel(Form)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.label_azimuth = QtWidgets.QLabel(Form)
        self.label_azimuth.setObjectName("label_azimuth")
        self.label_azimuth.setMinimumSize(QtCore.QSize(75,0))
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.label_azimuth)
        self.label_7 = QtWidgets.QLabel(Form)
        self.label_7.setObjectName("label_7")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_7)
        self.label_amplitude = QtWidgets.QLabel(Form)
        self.label_amplitude.setObjectName("label_amplitude")
        self.label_amplitude.setMinimumSize(QtCore.QSize(75,0))
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.label_amplitude)
        self.label_9 = QtWidgets.QLabel(Form)
        self.label_9.setObjectName("label_9")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_9)
        self.label_confidence = QtWidgets.QLabel(Form)
        self.label_confidence.setObjectName("label_confidence")
        self.label_confidence.setMinimumSize(QtCore.QSize(75,0))
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.label_confidence)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.formLayout.setItem(3, QtWidgets.QFormLayout.LabelRole, spacerItem)
        self.verticalLayout.addLayout(self.formLayout)
        self.gridLayout.addLayout(self.verticalLayout, 0, 3, 1, 1)

        self.compass_VLayout = QtWidgets.QVBoxLayout()
        self.compass_VLayout.setObjectName("compass_VLayout")
        self.gridLayout.addLayout(self.compass_VLayout, 0, 2, 1, 1)

        self.channel_VLayout = QtWidgets.QVBoxLayout()
        self.channel_VLayout.setObjectName("channel_VLayout")
        self.gridLayout.addLayout(self.channel_VLayout, 0, 0, 1, 1)

        self.VLayout = QtWidgets.QVBoxLayout()
        self.VLayout.setContentsMargins(10, -1, -1, -1)
        self.VLayout.setObjectName("VLayout")
        self.control_layout = QtWidgets.QGridLayout()
        self.control_layout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.control_layout.setContentsMargins(-1, 5, -1, 10)
        self.control_layout.setVerticalSpacing(10)
        self.control_layout.setObjectName("control_layout")
        self.label = QtWidgets.QLabel(Form)
        self.label.setObjectName("label")
        self.control_layout.addWidget(self.label, 1, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setObjectName("label_3")
        self.control_layout.addWidget(self.label_3, 4, 0, 1, 1)
        self.comboBox_gain = QtWidgets.QComboBox(Form)
        self.comboBox_gain.setEditable(False)
        self.comboBox_gain.setObjectName("comboBox_gain")
        self.control_layout.addWidget(self.comboBox_gain, 2, 1, 1, 2)
        self.doubleSpinBox_bandwidth = QtWidgets.QDoubleSpinBox(Form)
        self.doubleSpinBox_bandwidth.setMinimum(1.0)
        self.doubleSpinBox_bandwidth.setMaximum(100.0)
        self.doubleSpinBox_bandwidth.setProperty("value", 25)
        self.doubleSpinBox_bandwidth.setObjectName("doubleSpinBox_bandwidth")
        self.control_layout.addWidget(self.doubleSpinBox_bandwidth, 3, 1, 1, 2)
        self.label_4 = QtWidgets.QLabel(Form)
        self.label_4.setObjectName("label_4")
        self.control_layout.addWidget(self.label_4, 3, 0, 1, 1)
        self.pushButton_stop = QtWidgets.QPushButton(Form)
        self.pushButton_stop.setObjectName("pushButton_stop")
        self.control_layout.addWidget(self.pushButton_stop, 5, 2, 1, 1)
        self.pushButton_start = QtWidgets.QPushButton(Form)
        self.pushButton_start.setObjectName("pushButton_start")
        self.control_layout.addWidget(self.pushButton_start, 5, 1, 1, 1)

#        self.pushButton_test = QtWidgets.QPushButton(Form)
#        self.pushButton_test.setObjectName("pushButton_test")
#        self.control_layout.addWidget(self.pushButton_test, 5, 3, 1, 1)

        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setObjectName("label_2")
        self.control_layout.addWidget(self.label_2, 2, 0, 1, 1)
        self.label_meter = QtWidgets.QLabel(Form)
        self.label_meter.setObjectName("label_meter")
        self.control_layout.addWidget(self.label_meter, 4, 1, 1, 2)
        
        
        
        """
        self.doubleSpinBox_antenna_space = QtWidgets.QDoubleSpinBox(Form)
        self.doubleSpinBox_antenna_space.setMaximum(10.0)
        self.doubleSpinBox_antenna_space.setSingleStep(1.0)
        self.doubleSpinBox_antenna_space.setProperty("value", 0.26)
        self.doubleSpinBox_antenna_space.setObjectName("doubleSpinBox_antenna_space")
        self.control_layout.addWidget(self.doubleSpinBox_antenna_space, 4, 1, 1, 2)
        """
        self.doubleSpinBox_freq = QtWidgets.QDoubleSpinBox(Form)
        self.doubleSpinBox_freq.setDecimals(3)
        self.doubleSpinBox_freq.setMinimum(30.0)
        self.doubleSpinBox_freq.setMaximum(10000.0)        
        self.doubleSpinBox_freq.setObjectName("doubleSpinBox_freq")
        self.control_layout.addWidget(self.doubleSpinBox_freq, 1, 1, 1, 2)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.control_layout.addItem(spacerItem1, 0, 1, 1, 1)
        self.VLayout.addLayout(self.control_layout)
        self.gridLayout.addLayout(self.VLayout, 0, 5, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 0, 1, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem3, 0, 4, 1, 1)
        
        
#        self.gridLayout_sync = QtWidgets.QGridLayout()
#        self.gridLayout_sync.setObjectName("gridLayout_sync")
#        self.gridLayout.addLayout(self.gridLayout_sync, 0, 7, 1, 1)

        self.retranslateUi(Form)
        self.comboBox_gain.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label_5.setText(_translate("Form", "Azimuth"))
        self.label_azimuth.setText(_translate("Form", "----------"))
        self.label_7.setText(_translate("Form", "Amplitude"))
        self.label_amplitude.setText(_translate("Form", "----------"))
        self.label_9.setText(_translate("Form", "Cofidence"))
        self.label_confidence.setText(_translate("Form", "----------"))
        self.label.setText(_translate("Form", "Frequency (MHz)"))
        self.label_3.setText(_translate("Form", "Antenna Radius (m)"))
        self.label_4.setText(_translate("Form", "Bandwidth (kHz)"))
        self.pushButton_stop.setText(_translate("Form", "Stop"))
        self.pushButton_start.setText(_translate("Form", "Start"))

#        self.pushButton_test.setText(_translate("Form", "Close"))

        self.label_2.setText(_translate("Form", "Gain (dB)"))
