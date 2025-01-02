# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'E:\Programming\MainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1280, 720)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setIconSize(QtCore.QSize(25, 25))
        self.tabWidget.setObjectName("tabWidget")
        self.spectrum_tab = QtWidgets.QWidget()
        self.spectrum_tab.setObjectName("spectrum_tab")
        self.verticalLayout_Spectrum = QtWidgets.QVBoxLayout(self.spectrum_tab)
        self.verticalLayout_Spectrum.setObjectName("verticalLayout_Spectrum")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../Downloads/spectrum.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.tabWidget.addTab(self.spectrum_tab, icon, "")
        self.analysis_tab = QtWidgets.QWidget()
        self.analysis_tab.setObjectName("analysis_tab")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.analysis_tab)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.analysis_groupbox = QtWidgets.QGroupBox(self.analysis_tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.analysis_groupbox.sizePolicy().hasHeightForWidth())
        self.analysis_groupbox.setSizePolicy(sizePolicy)
        self.analysis_groupbox.setMinimumSize(QtCore.QSize(0, 350))
        self.analysis_groupbox.setObjectName("analysis_groupbox")
        self.verticalLayout_analysis = QtWidgets.QVBoxLayout(self.analysis_groupbox)
        self.verticalLayout_analysis.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.verticalLayout_analysis.setObjectName("verticalLayout_analysis")
        self.gridLayout_2.addWidget(self.analysis_groupbox, 0, 0, 1, 1)
        self.df_groupbox = QtWidgets.QGroupBox(self.analysis_tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.df_groupbox.sizePolicy().hasHeightForWidth())
        self.df_groupbox.setSizePolicy(sizePolicy)
        self.df_groupbox.setMinimumSize(QtCore.QSize(0, 300))
        self.df_groupbox.setObjectName("df_groupbox")
        self.verticalLayout_DF = QtWidgets.QVBoxLayout(self.df_groupbox)
        self.verticalLayout_DF.setObjectName("verticalLayout_DF")
        self.gridLayout_2.addWidget(self.df_groupbox, 1, 0, 1, 1)
        self.tabWidget.addTab(self.analysis_tab, "")
        
        self.map_tab = QtWidgets.QWidget()
        self.map_tab.setObjectName("map_tab")
        self.verticalLayout_Map = QtWidgets.QVBoxLayout(self.map_tab)
        self.verticalLayout_Map.setObjectName("verticalLayout_Map")
        self.tabWidget.addTab(self.map_tab,"")
        
        
        
        self.horizontalLayout.addWidget(self.tabWidget)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.action_Settings = QtWidgets.QAction(MainWindow)
        self.action_Settings.setObjectName("action_Settings")
        self.action_Quit = QtWidgets.QAction(MainWindow)
        self.action_Quit.setObjectName("action_Quit")
        self.action_About = QtWidgets.QAction(MainWindow)
        self.action_About.setObjectName("action_About")

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Kerberos SDR"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.spectrum_tab), _translate("MainWindow", "Wideband Spectrum"))
        self.analysis_groupbox.setTitle(_translate("MainWindow", "  Signal Analysis  "))
        self.df_groupbox.setTitle(_translate("MainWindow", "   Direction Finding   "))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.analysis_tab), _translate("MainWindow", "Narrowband Analysis"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.map_tab), _translate("MainWindow", "Map"))
        self.action_Settings.setText(_translate("MainWindow", "&Settings..."))
        self.action_Quit.setText(_translate("MainWindow", "&Quit"))
        self.action_Quit.setShortcut(_translate("MainWindow", "Ctrl+Q"))
        self.action_About.setText(_translate("MainWindow", "&About"))
        
  

