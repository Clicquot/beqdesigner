# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'beq.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1550, 956)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.widgetGridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.widgetGridLayout.setObjectName("widgetGridLayout")
        self.panes = QtWidgets.QHBoxLayout()
        self.panes.setSpacing(9)
        self.panes.setObjectName("panes")
        self.leftPane = QtWidgets.QGridLayout()
        self.leftPane.setObjectName("leftPane")
        self.referenceLabel = QtWidgets.QLabel(self.centralwidget)
        self.referenceLabel.setObjectName("referenceLabel")
        self.leftPane.addWidget(self.referenceLabel, 0, 0, 1, 1)
        self.mainChart = MplWidget(self.centralwidget)
        self.mainChart.setObjectName("mainChart")
        self.leftPane.addWidget(self.mainChart, 1, 0, 1, 6)
        self.limitsButton = QtWidgets.QToolButton(self.centralwidget)
        self.limitsButton.setObjectName("limitsButton")
        self.leftPane.addWidget(self.limitsButton, 0, 4, 1, 1)
        self.signalReference = QtWidgets.QComboBox(self.centralwidget)
        self.signalReference.setObjectName("signalReference")
        self.signalReference.addItem("")
        self.leftPane.addWidget(self.signalReference, 0, 1, 1, 1)
        self.filterReference = QtWidgets.QComboBox(self.centralwidget)
        self.filterReference.setObjectName("filterReference")
        self.filterReference.addItem("")
        self.leftPane.addWidget(self.filterReference, 0, 2, 1, 1)
        self.showValuesButton = QtWidgets.QToolButton(self.centralwidget)
        self.showValuesButton.setObjectName("showValuesButton")
        self.leftPane.addWidget(self.showValuesButton, 0, 3, 1, 1)
        self.leftPane.setColumnStretch(1, 1)
        self.leftPane.setColumnStretch(2, 1)
        self.panes.addLayout(self.leftPane)
        self.rightPane = QtWidgets.QGridLayout()
        self.rightPane.setObjectName("rightPane")
        self.addSignalButton = QtWidgets.QPushButton(self.centralwidget)
        self.addSignalButton.setObjectName("addSignalButton")
        self.rightPane.addWidget(self.addSignalButton, 1, 0, 1, 1)
        self.filtersLabel = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.filtersLabel.setFont(font)
        self.filtersLabel.setFrameShape(QtWidgets.QFrame.Box)
        self.filtersLabel.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.filtersLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.filtersLabel.setObjectName("filtersLabel")
        self.rightPane.addWidget(self.filtersLabel, 3, 0, 1, 3)
        self.signalsLabel = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.signalsLabel.setFont(font)
        self.signalsLabel.setFrameShape(QtWidgets.QFrame.Box)
        self.signalsLabel.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.signalsLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.signalsLabel.setObjectName("signalsLabel")
        self.rightPane.addWidget(self.signalsLabel, 0, 0, 1, 3)
        self.loadPreset1 = QtWidgets.QPushButton(self.centralwidget)
        self.loadPreset1.setEnabled(True)
        self.loadPreset1.setObjectName("loadPreset1")
        self.rightPane.addWidget(self.loadPreset1, 4, 0, 1, 1)
        self.loadPreset2 = QtWidgets.QPushButton(self.centralwidget)
        self.loadPreset2.setEnabled(True)
        self.loadPreset2.setObjectName("loadPreset2")
        self.rightPane.addWidget(self.loadPreset2, 4, 1, 1, 1)
        self.signalView = QtWidgets.QTableView(self.centralwidget)
        self.signalView.setObjectName("signalView")
        self.rightPane.addWidget(self.signalView, 2, 0, 1, 3)
        self.addFilterButton = QtWidgets.QPushButton(self.centralwidget)
        self.addFilterButton.setEnabled(True)
        self.addFilterButton.setObjectName("addFilterButton")
        self.rightPane.addWidget(self.addFilterButton, 5, 0, 1, 1)
        self.loadPreset3 = QtWidgets.QPushButton(self.centralwidget)
        self.loadPreset3.setEnabled(True)
        self.loadPreset3.setObjectName("loadPreset3")
        self.rightPane.addWidget(self.loadPreset3, 4, 2, 1, 1)
        self.editFilterButton = QtWidgets.QPushButton(self.centralwidget)
        self.editFilterButton.setEnabled(False)
        self.editFilterButton.setFlat(False)
        self.editFilterButton.setObjectName("editFilterButton")
        self.rightPane.addWidget(self.editFilterButton, 5, 1, 1, 1)
        self.deleteFilterButton = QtWidgets.QPushButton(self.centralwidget)
        self.deleteFilterButton.setEnabled(False)
        self.deleteFilterButton.setObjectName("deleteFilterButton")
        self.rightPane.addWidget(self.deleteFilterButton, 5, 2, 1, 1)
        self.deleteSignalButton = QtWidgets.QPushButton(self.centralwidget)
        self.deleteSignalButton.setEnabled(False)
        self.deleteSignalButton.setObjectName("deleteSignalButton")
        self.rightPane.addWidget(self.deleteSignalButton, 1, 2, 1, 1)
        self.filterView = QtWidgets.QTableView(self.centralwidget)
        self.filterView.setObjectName("filterView")
        self.rightPane.addWidget(self.filterView, 6, 0, 1, 3)
        self.showLegend = QtWidgets.QCheckBox(self.centralwidget)
        self.showLegend.setChecked(True)
        self.showLegend.setObjectName("showLegend")
        self.rightPane.addWidget(self.showLegend, 9, 2, 1, 1)
        self.showFilters = QtWidgets.QComboBox(self.centralwidget)
        self.showFilters.setObjectName("showFilters")
        self.rightPane.addWidget(self.showFilters, 9, 1, 1, 1)
        self.showFiltersLabel = QtWidgets.QLabel(self.centralwidget)
        self.showFiltersLabel.setObjectName("showFiltersLabel")
        self.rightPane.addWidget(self.showFiltersLabel, 9, 0, 1, 1)
        self.panes.addLayout(self.rightPane)
        self.panes.setStretch(0, 3)
        self.panes.setStretch(1, 1)
        self.widgetGridLayout.addLayout(self.panes, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1550, 31))
        self.menubar.setObjectName("menubar")
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        self.menuSettings = QtWidgets.QMenu(self.menubar)
        self.menuSettings.setObjectName("menuSettings")
        self.menuPresets = QtWidgets.QMenu(self.menuSettings)
        self.menuPresets.setObjectName("menuPresets")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionShow_Logs = QtWidgets.QAction(MainWindow)
        self.actionShow_Logs.setObjectName("actionShow_Logs")
        self.actionPreferences = QtWidgets.QAction(MainWindow)
        self.actionPreferences.setObjectName("actionPreferences")
        self.actionExtract_Audio = QtWidgets.QAction(MainWindow)
        self.actionExtract_Audio.setObjectName("actionExtract_Audio")
        self.actionPresets = QtWidgets.QAction(MainWindow)
        self.actionPresets.setObjectName("actionPresets")
        self.actionSave_Preset_1 = QtWidgets.QAction(MainWindow)
        self.actionSave_Preset_1.setObjectName("actionSave_Preset_1")
        self.actionClear_Preset_1 = QtWidgets.QAction(MainWindow)
        self.actionClear_Preset_1.setObjectName("actionClear_Preset_1")
        self.actionSave_Preset_2 = QtWidgets.QAction(MainWindow)
        self.actionSave_Preset_2.setObjectName("actionSave_Preset_2")
        self.actionClear_Preset_2 = QtWidgets.QAction(MainWindow)
        self.actionClear_Preset_2.setObjectName("actionClear_Preset_2")
        self.actionSave_Preset_3 = QtWidgets.QAction(MainWindow)
        self.actionSave_Preset_3.setObjectName("actionSave_Preset_3")
        self.actionClear_Preset_3 = QtWidgets.QAction(MainWindow)
        self.actionClear_Preset_3.setObjectName("actionClear_Preset_3")
        self.actionSave_Chart = QtWidgets.QAction(MainWindow)
        self.actionSave_Chart.setObjectName("actionSave_Chart")
        self.actionExport_Biquad = QtWidgets.QAction(MainWindow)
        self.actionExport_Biquad.setObjectName("actionExport_Biquad")
        self.actionLoad_Filter = QtWidgets.QAction(MainWindow)
        self.actionLoad_Filter.setObjectName("actionLoad_Filter")
        self.actionSave_Filter = QtWidgets.QAction(MainWindow)
        self.actionSave_Filter.setEnabled(False)
        self.actionSave_Filter.setObjectName("actionSave_Filter")
        self.menuHelp.addAction(self.actionShow_Logs)
        self.menuPresets.addAction(self.actionSave_Preset_1)
        self.menuPresets.addAction(self.actionSave_Preset_2)
        self.menuPresets.addAction(self.actionSave_Preset_3)
        self.menuPresets.addSeparator()
        self.menuPresets.addAction(self.actionClear_Preset_1)
        self.menuPresets.addAction(self.actionClear_Preset_2)
        self.menuPresets.addAction(self.actionClear_Preset_3)
        self.menuSettings.addAction(self.actionPreferences)
        self.menuSettings.addSeparator()
        self.menuSettings.addAction(self.menuPresets.menuAction())
        self.menuFile.addAction(self.actionExtract_Audio)
        self.menuFile.addAction(self.actionSave_Chart)
        self.menuFile.addAction(self.actionExport_Biquad)
        self.menuFile.addAction(self.actionSave_Filter)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuSettings.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        self.addFilterButton.clicked.connect(MainWindow.addFilter)
        self.deleteFilterButton.clicked.connect(MainWindow.deleteFilter)
        self.editFilterButton.clicked.connect(MainWindow.editFilter)
        self.addSignalButton.clicked.connect(MainWindow.addSignal)
        self.deleteSignalButton.clicked.connect(MainWindow.deleteSignal)
        self.signalReference.currentIndexChanged['int'].connect(MainWindow.normaliseSignalMagnitude)
        self.limitsButton.clicked.connect(MainWindow.showLimits)
        self.filterReference.currentIndexChanged['int'].connect(MainWindow.normaliseFilterMagnitude)
        self.showValuesButton.clicked.connect(MainWindow.showValues)
        self.showLegend.clicked.connect(MainWindow.changeLegendVisibility)
        self.showFilters.currentTextChanged['QString'].connect(MainWindow.changeFilterVisibility)
        self.loadPreset1.clicked.connect(MainWindow.handlePreset1)
        self.loadPreset2.clicked.connect(MainWindow.handlePreset2)
        self.loadPreset3.clicked.connect(MainWindow.handlePreset3)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "BEQ Designer"))
        self.referenceLabel.setText(_translate("MainWindow", "Reference:"))
        self.limitsButton.setText(_translate("MainWindow", "..."))
        self.signalReference.setItemText(0, _translate("MainWindow", "None"))
        self.filterReference.setItemText(0, _translate("MainWindow", "None"))
        self.showValuesButton.setText(_translate("MainWindow", "..."))
        self.addSignalButton.setText(_translate("MainWindow", "Add"))
        self.addSignalButton.setShortcut(_translate("MainWindow", "Ctrl+Shift+="))
        self.filtersLabel.setText(_translate("MainWindow", "Filters"))
        self.signalsLabel.setText(_translate("MainWindow", "Signals"))
        self.loadPreset1.setText(_translate("MainWindow", "Preset 1"))
        self.loadPreset2.setText(_translate("MainWindow", "Preset 2"))
        self.addFilterButton.setText(_translate("MainWindow", "Add"))
        self.addFilterButton.setShortcut(_translate("MainWindow", "Ctrl+="))
        self.loadPreset3.setText(_translate("MainWindow", "Preset 3"))
        self.editFilterButton.setText(_translate("MainWindow", "Edit"))
        self.deleteFilterButton.setText(_translate("MainWindow", "Delete"))
        self.deleteFilterButton.setShortcut(_translate("MainWindow", "Ctrl+-"))
        self.deleteSignalButton.setText(_translate("MainWindow", "Delete"))
        self.showLegend.setText(_translate("MainWindow", "Show Legend"))
        self.showFiltersLabel.setText(_translate("MainWindow", "Show Filters?"))
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        self.menuSettings.setTitle(_translate("MainWindow", "Settings"))
        self.menuPresets.setTitle(_translate("MainWindow", "Presets"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.actionShow_Logs.setText(_translate("MainWindow", "Show Logs"))
        self.actionShow_Logs.setShortcut(_translate("MainWindow", "Ctrl+L"))
        self.actionPreferences.setText(_translate("MainWindow", "Preferences"))
        self.actionPreferences.setShortcut(_translate("MainWindow", "Ctrl+P"))
        self.actionExtract_Audio.setText(_translate("MainWindow", "Extract Audio"))
        self.actionExtract_Audio.setShortcut(_translate("MainWindow", "Ctrl+E"))
        self.actionPresets.setText(_translate("MainWindow", "Presets"))
        self.actionSave_Preset_1.setText(_translate("MainWindow", "Save Preset 1"))
        self.actionSave_Preset_1.setShortcut(_translate("MainWindow", "Ctrl+Shift+1"))
        self.actionClear_Preset_1.setText(_translate("MainWindow", "Clear Preset 1"))
        self.actionSave_Preset_2.setText(_translate("MainWindow", "Save Preset 2"))
        self.actionSave_Preset_2.setShortcut(_translate("MainWindow", "Ctrl+Shift+2"))
        self.actionClear_Preset_2.setText(_translate("MainWindow", "Clear Preset 2"))
        self.actionSave_Preset_3.setText(_translate("MainWindow", "Save Preset 3"))
        self.actionSave_Preset_3.setShortcut(_translate("MainWindow", "Ctrl+Shift+3"))
        self.actionClear_Preset_3.setText(_translate("MainWindow", "Clear Preset 3"))
        self.actionSave_Chart.setText(_translate("MainWindow", "Save Chart"))
        self.actionSave_Chart.setShortcut(_translate("MainWindow", "Ctrl+S"))
        self.actionExport_Biquad.setText(_translate("MainWindow", "Export Biquad"))
        self.actionExport_Biquad.setShortcut(_translate("MainWindow", "Ctrl+B"))
        self.actionLoad_Filter.setText(_translate("MainWindow", "Load Filter"))
        self.actionSave_Filter.setText(_translate("MainWindow", "Save Filter"))

from mpl import MplWidget
