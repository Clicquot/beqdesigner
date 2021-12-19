# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'signal.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_addSignalDialog(object):
    def setupUi(self, addSignalDialog):
        addSignalDialog.setObjectName("addSignalDialog")
        addSignalDialog.resize(1392, 748)
        self.verticalLayout = QtWidgets.QVBoxLayout(addSignalDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.panesLayout = QtWidgets.QGridLayout()
        self.panesLayout.setObjectName("panesLayout")
        self.buttonBox = QtWidgets.QDialogButtonBox(addSignalDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.panesLayout.addWidget(self.buttonBox, 4, 0, 1, 1)
        self.linkedSignal = QtWidgets.QCheckBox(addSignalDialog)
        self.linkedSignal.setEnabled(True)
        self.linkedSignal.setObjectName("linkedSignal")
        self.panesLayout.addWidget(self.linkedSignal, 3, 0, 1, 1)
        self.filterSelectLayout = QtWidgets.QGridLayout()
        self.filterSelectLayout.setObjectName("filterSelectLayout")
        self.filterSelectLabel = QtWidgets.QLabel(addSignalDialog)
        self.filterSelectLabel.setObjectName("filterSelectLabel")
        self.filterSelectLayout.addWidget(self.filterSelectLabel, 0, 0, 1, 1)
        self.filterSelect = QtWidgets.QComboBox(addSignalDialog)
        self.filterSelect.setObjectName("filterSelect")
        self.filterSelect.addItem("")
        self.filterSelectLayout.addWidget(self.filterSelect, 0, 1, 1, 1)
        self.filterSelectLayout.setColumnStretch(1, 1)
        self.panesLayout.addLayout(self.filterSelectLayout, 2, 0, 1, 1)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.signalTypeTabs = QtWidgets.QTabWidget(addSignalDialog)
        self.signalTypeTabs.setObjectName("signalTypeTabs")
        self.wavTab = QtWidgets.QWidget()
        self.wavTab.setObjectName("wavTab")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.wavTab)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.wavGridLayout = QtWidgets.QGridLayout()
        self.wavGridLayout.setObjectName("wavGridLayout")
        self.wavStartTime = QtWidgets.QTimeEdit(self.wavTab)
        self.wavStartTime.setEnabled(False)
        self.wavStartTime.setTime(QtCore.QTime(0, 0, 0))
        self.wavStartTime.setObjectName("wavStartTime")
        self.wavGridLayout.addWidget(self.wavStartTime, 4, 1, 1, 1)
        self.wavFile = QtWidgets.QLineEdit(self.wavTab)
        self.wavFile.setEnabled(False)
        self.wavFile.setReadOnly(True)
        self.wavFile.setObjectName("wavFile")
        self.wavGridLayout.addWidget(self.wavFile, 1, 1, 1, 1)
        self.wavFs = QtWidgets.QLineEdit(self.wavTab)
        self.wavFs.setEnabled(False)
        self.wavFs.setObjectName("wavFs")
        self.wavGridLayout.addWidget(self.wavFs, 2, 1, 1, 1)
        self.wavSignalName = QtWidgets.QLineEdit(self.wavTab)
        self.wavSignalName.setEnabled(False)
        self.wavSignalName.setObjectName("wavSignalName")
        self.wavGridLayout.addWidget(self.wavSignalName, 6, 1, 1, 1)
        self.decimate = QtWidgets.QCheckBox(self.wavTab)
        self.decimate.setChecked(True)
        self.decimate.setObjectName("decimate")
        self.wavGridLayout.addWidget(self.decimate, 9, 1, 1, 1)
        self.wavFileLabel = QtWidgets.QLabel(self.wavTab)
        self.wavFileLabel.setObjectName("wavFileLabel")
        self.wavGridLayout.addWidget(self.wavFileLabel, 1, 0, 1, 1)
        self.loadAllChannels = QtWidgets.QCheckBox(self.wavTab)
        self.loadAllChannels.setChecked(True)
        self.loadAllChannels.setObjectName("loadAllChannels")
        self.wavGridLayout.addWidget(self.loadAllChannels, 8, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.wavGridLayout.addItem(spacerItem, 10, 1, 1, 1)
        self.applyTimeRangeButton = QtWidgets.QToolButton(self.wavTab)
        self.applyTimeRangeButton.setObjectName("applyTimeRangeButton")
        self.wavGridLayout.addWidget(self.applyTimeRangeButton, 5, 2, 1, 1)
        self.wavStartTimeLabel = QtWidgets.QLabel(self.wavTab)
        self.wavStartTimeLabel.setObjectName("wavStartTimeLabel")
        self.wavGridLayout.addWidget(self.wavStartTimeLabel, 4, 0, 1, 1)
        self.wavEndTime = QtWidgets.QTimeEdit(self.wavTab)
        self.wavEndTime.setEnabled(False)
        self.wavEndTime.setObjectName("wavEndTime")
        self.wavGridLayout.addWidget(self.wavEndTime, 5, 1, 1, 1)
        self.wavSignalNameLabel = QtWidgets.QLabel(self.wavTab)
        self.wavSignalNameLabel.setObjectName("wavSignalNameLabel")
        self.wavGridLayout.addWidget(self.wavSignalNameLabel, 6, 0, 1, 1)
        self.wavFilePicker = QtWidgets.QToolButton(self.wavTab)
        self.wavFilePicker.setObjectName("wavFilePicker")
        self.wavGridLayout.addWidget(self.wavFilePicker, 1, 2, 1, 1)
        self.wavChannelSelector = QtWidgets.QComboBox(self.wavTab)
        self.wavChannelSelector.setEnabled(False)
        self.wavChannelSelector.setObjectName("wavChannelSelector")
        self.wavGridLayout.addWidget(self.wavChannelSelector, 3, 1, 1, 1)
        self.wavEndTimeLabel = QtWidgets.QLabel(self.wavTab)
        self.wavEndTimeLabel.setObjectName("wavEndTimeLabel")
        self.wavGridLayout.addWidget(self.wavEndTimeLabel, 5, 0, 1, 1)
        self.wavFsLabel = QtWidgets.QLabel(self.wavTab)
        self.wavFsLabel.setObjectName("wavFsLabel")
        self.wavGridLayout.addWidget(self.wavFsLabel, 2, 0, 1, 1)
        self.wavChannelLabel = QtWidgets.QLabel(self.wavTab)
        self.wavChannelLabel.setObjectName("wavChannelLabel")
        self.wavGridLayout.addWidget(self.wavChannelLabel, 3, 0, 1, 1)
        self.gainOffset = QtWidgets.QDoubleSpinBox(self.wavTab)
        self.gainOffset.setEnabled(False)
        self.gainOffset.setMinimum(-100.0)
        self.gainOffset.setMaximum(100.0)
        self.gainOffset.setSingleStep(0.01)
        self.gainOffset.setObjectName("gainOffset")
        self.wavGridLayout.addWidget(self.gainOffset, 7, 1, 1, 1)
        self.gainOffsetLabel = QtWidgets.QLabel(self.wavTab)
        self.gainOffsetLabel.setObjectName("gainOffsetLabel")
        self.wavGridLayout.addWidget(self.gainOffsetLabel, 7, 0, 1, 1)
        self.gridLayout_3.addLayout(self.wavGridLayout, 0, 0, 1, 1)
        self.signalTypeTabs.addTab(self.wavTab, "")
        self.frdTab = QtWidgets.QWidget()
        self.frdTab.setObjectName("frdTab")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.frdTab)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.frdGridLayout = QtWidgets.QGridLayout()
        self.frdGridLayout.setObjectName("frdGridLayout")
        self.frdFsLabel = QtWidgets.QLabel(self.frdTab)
        self.frdFsLabel.setObjectName("frdFsLabel")
        self.frdGridLayout.addWidget(self.frdFsLabel, 2, 0, 1, 1)
        self.frdFs = QtWidgets.QSpinBox(self.frdTab)
        self.frdFs.setEnabled(False)
        self.frdFs.setMinimum(100)
        self.frdFs.setMaximum(96000)
        self.frdFs.setSingleStep(100)
        self.frdFs.setProperty("value", 48000)
        self.frdFs.setObjectName("frdFs")
        self.frdGridLayout.addWidget(self.frdFs, 2, 1, 1, 1)
        self.frdAvgFileLabel = QtWidgets.QLabel(self.frdTab)
        self.frdAvgFileLabel.setObjectName("frdAvgFileLabel")
        self.frdGridLayout.addWidget(self.frdAvgFileLabel, 0, 0, 1, 1)
        self.frdAvgFile = QtWidgets.QLineEdit(self.frdTab)
        self.frdAvgFile.setEnabled(False)
        self.frdAvgFile.setObjectName("frdAvgFile")
        self.frdGridLayout.addWidget(self.frdAvgFile, 0, 1, 1, 1)
        self.frdAvgFilePicker = QtWidgets.QToolButton(self.frdTab)
        self.frdAvgFilePicker.setObjectName("frdAvgFilePicker")
        self.frdGridLayout.addWidget(self.frdAvgFilePicker, 0, 2, 1, 1)
        self.frdSignalNameLabel = QtWidgets.QLabel(self.frdTab)
        self.frdSignalNameLabel.setObjectName("frdSignalNameLabel")
        self.frdGridLayout.addWidget(self.frdSignalNameLabel, 3, 0, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.frdGridLayout.addItem(spacerItem1, 4, 1, 1, 1)
        self.frdSignalName = QtWidgets.QLineEdit(self.frdTab)
        self.frdSignalName.setEnabled(False)
        self.frdSignalName.setObjectName("frdSignalName")
        self.frdGridLayout.addWidget(self.frdSignalName, 3, 1, 1, 1)
        self.frdPeakFileLabel = QtWidgets.QLabel(self.frdTab)
        self.frdPeakFileLabel.setObjectName("frdPeakFileLabel")
        self.frdGridLayout.addWidget(self.frdPeakFileLabel, 1, 0, 1, 1)
        self.frdPeakFilePicker = QtWidgets.QToolButton(self.frdTab)
        self.frdPeakFilePicker.setObjectName("frdPeakFilePicker")
        self.frdGridLayout.addWidget(self.frdPeakFilePicker, 1, 2, 1, 1)
        self.frdPeakFile = QtWidgets.QLineEdit(self.frdTab)
        self.frdPeakFile.setEnabled(False)
        self.frdPeakFile.setObjectName("frdPeakFile")
        self.frdGridLayout.addWidget(self.frdPeakFile, 1, 1, 1, 1)
        self.gridLayout_5.addLayout(self.frdGridLayout, 0, 0, 1, 1)
        self.signalTypeTabs.addTab(self.frdTab, "")
        self.pulseTab = QtWidgets.QWidget()
        self.pulseTab.setObjectName("pulseTab")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.pulseTab)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.pulseFsLabel = QtWidgets.QLabel(self.pulseTab)
        self.pulseFsLabel.setObjectName("pulseFsLabel")
        self.gridLayout_2.addWidget(self.pulseFsLabel, 2, 0, 1, 1)
        self.pulsePrefixLabel = QtWidgets.QLabel(self.pulseTab)
        self.pulsePrefixLabel.setObjectName("pulsePrefixLabel")
        self.gridLayout_2.addWidget(self.pulsePrefixLabel, 1, 0, 1, 1)
        self.presetsHeaderLabel = QtWidgets.QLabel(self.pulseTab)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.presetsHeaderLabel.setFont(font)
        self.presetsHeaderLabel.setFrameShape(QtWidgets.QFrame.Box)
        self.presetsHeaderLabel.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.presetsHeaderLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.presetsHeaderLabel.setObjectName("presetsHeaderLabel")
        self.gridLayout_2.addWidget(self.presetsHeaderLabel, 0, 0, 1, 3)
        self.pulseChannels = QtWidgets.QListWidget(self.pulseTab)
        self.pulseChannels.setObjectName("pulseChannels")
        self.gridLayout_2.addWidget(self.pulseChannels, 3, 0, 1, 3)
        self.pulseFs = QtWidgets.QComboBox(self.pulseTab)
        self.pulseFs.setObjectName("pulseFs")
        self.pulseFs.addItem("")
        self.pulseFs.addItem("")
        self.gridLayout_2.addWidget(self.pulseFs, 2, 1, 1, 2)
        self.pulsePrefix = QtWidgets.QLineEdit(self.pulseTab)
        self.pulsePrefix.setEnabled(True)
        self.pulsePrefix.setReadOnly(False)
        self.pulsePrefix.setObjectName("pulsePrefix")
        self.gridLayout_2.addWidget(self.pulsePrefix, 1, 1, 1, 2)
        self.verticalLayout_2.addLayout(self.gridLayout_2)
        self.signalTypeTabs.addTab(self.pulseTab, "")
        self.gridLayout.addWidget(self.signalTypeTabs, 7, 1, 1, 1)
        self.panesLayout.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.previewChart = MplWidget(addSignalDialog)
        self.previewChart.setObjectName("previewChart")
        self.panesLayout.addWidget(self.previewChart, 0, 1, 6, 1)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.panesLayout.addItem(spacerItem2, 5, 0, 1, 1)
        self.panesLayout.setColumnStretch(1, 1)
        self.verticalLayout.addLayout(self.panesLayout)

        self.retranslateUi(addSignalDialog)
        self.signalTypeTabs.setCurrentIndex(0)
        self.buttonBox.rejected.connect(addSignalDialog.reject) # type: ignore
        self.buttonBox.accepted.connect(addSignalDialog.accept) # type: ignore
        self.wavFilePicker.clicked.connect(addSignalDialog.selectFile) # type: ignore
        self.signalTypeTabs.currentChanged['int'].connect(addSignalDialog.changeLoader) # type: ignore
        self.frdAvgFilePicker.clicked.connect(addSignalDialog.selectAvgFile) # type: ignore
        self.frdPeakFilePicker.clicked.connect(addSignalDialog.selectPeakFile) # type: ignore
        self.wavSignalName.textChanged['QString'].connect(addSignalDialog.enableOk) # type: ignore
        self.frdSignalName.textChanged['QString'].connect(addSignalDialog.enableOk) # type: ignore
        self.filterSelect.currentIndexChanged['int'].connect(addSignalDialog.masterFilterChanged) # type: ignore
        self.wavChannelSelector.currentTextChanged['QString'].connect(addSignalDialog.previewChannel) # type: ignore
        self.applyTimeRangeButton.clicked.connect(addSignalDialog.limitTimeRange) # type: ignore
        self.wavStartTime.timeChanged['QTime'].connect(addSignalDialog.enableLimitTimeRangeButton) # type: ignore
        self.wavEndTime.timeChanged['QTime'].connect(addSignalDialog.enableLimitTimeRangeButton) # type: ignore
        self.decimate.stateChanged['int'].connect(addSignalDialog.toggleDecimate) # type: ignore
        self.pulsePrefix.textChanged['QString'].connect(addSignalDialog.enableOk) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(addSignalDialog)
        addSignalDialog.setTabOrder(self.signalTypeTabs, self.wavFilePicker)
        addSignalDialog.setTabOrder(self.wavFilePicker, self.wavChannelSelector)
        addSignalDialog.setTabOrder(self.wavChannelSelector, self.wavStartTime)
        addSignalDialog.setTabOrder(self.wavStartTime, self.wavEndTime)
        addSignalDialog.setTabOrder(self.wavEndTime, self.wavSignalName)
        addSignalDialog.setTabOrder(self.wavSignalName, self.loadAllChannels)
        addSignalDialog.setTabOrder(self.loadAllChannels, self.decimate)
        addSignalDialog.setTabOrder(self.decimate, self.filterSelect)
        addSignalDialog.setTabOrder(self.filterSelect, self.linkedSignal)
        addSignalDialog.setTabOrder(self.linkedSignal, self.wavFile)
        addSignalDialog.setTabOrder(self.wavFile, self.wavFs)
        addSignalDialog.setTabOrder(self.wavFs, self.frdFs)
        addSignalDialog.setTabOrder(self.frdFs, self.frdAvgFile)
        addSignalDialog.setTabOrder(self.frdAvgFile, self.frdAvgFilePicker)
        addSignalDialog.setTabOrder(self.frdAvgFilePicker, self.frdSignalName)
        addSignalDialog.setTabOrder(self.frdSignalName, self.frdPeakFilePicker)
        addSignalDialog.setTabOrder(self.frdPeakFilePicker, self.frdPeakFile)
        addSignalDialog.setTabOrder(self.frdPeakFile, self.previewChart)

    def retranslateUi(self, addSignalDialog):
        _translate = QtCore.QCoreApplication.translate
        addSignalDialog.setWindowTitle(_translate("addSignalDialog", "Load Signal"))
        self.linkedSignal.setText(_translate("addSignalDialog", "Linked Filter?"))
        self.filterSelectLabel.setText(_translate("addSignalDialog", "Copy Filter"))
        self.filterSelect.setItemText(0, _translate("addSignalDialog", "None"))
        self.wavStartTime.setDisplayFormat(_translate("addSignalDialog", "HH:mm:ss.zzz"))
        self.decimate.setText(_translate("addSignalDialog", "Resample?"))
        self.wavFileLabel.setText(_translate("addSignalDialog", "File"))
        self.loadAllChannels.setText(_translate("addSignalDialog", "Load All Channels?"))
        self.applyTimeRangeButton.setText(_translate("addSignalDialog", "..."))
        self.wavStartTimeLabel.setText(_translate("addSignalDialog", "Start"))
        self.wavEndTime.setDisplayFormat(_translate("addSignalDialog", "HH:mm:ss.zzz"))
        self.wavSignalNameLabel.setText(_translate("addSignalDialog", "Name"))
        self.wavFilePicker.setText(_translate("addSignalDialog", "..."))
        self.wavEndTimeLabel.setText(_translate("addSignalDialog", "End"))
        self.wavFsLabel.setText(_translate("addSignalDialog", "Fs"))
        self.wavChannelLabel.setText(_translate("addSignalDialog", "Channel"))
        self.gainOffset.setSuffix(_translate("addSignalDialog", " dB"))
        self.gainOffsetLabel.setText(_translate("addSignalDialog", "Offset"))
        self.signalTypeTabs.setTabText(self.signalTypeTabs.indexOf(self.wavTab), _translate("addSignalDialog", "AUDIO"))
        self.frdFsLabel.setText(_translate("addSignalDialog", "Fs"))
        self.frdAvgFileLabel.setText(_translate("addSignalDialog", "Avg"))
        self.frdAvgFilePicker.setText(_translate("addSignalDialog", "..."))
        self.frdSignalNameLabel.setText(_translate("addSignalDialog", "Name"))
        self.frdPeakFileLabel.setText(_translate("addSignalDialog", "Peak"))
        self.frdPeakFilePicker.setText(_translate("addSignalDialog", "..."))
        self.signalTypeTabs.setTabText(self.signalTypeTabs.indexOf(self.frdTab), _translate("addSignalDialog", "TXT"))
        self.pulseFsLabel.setText(_translate("addSignalDialog", "Fs"))
        self.pulsePrefixLabel.setText(_translate("addSignalDialog", "Prefix"))
        self.presetsHeaderLabel.setText(_translate("addSignalDialog", "Presets"))
        self.pulseFs.setItemText(0, _translate("addSignalDialog", "48 kHz"))
        self.pulseFs.setItemText(1, _translate("addSignalDialog", "96 kHz"))
        self.signalTypeTabs.setTabText(self.signalTypeTabs.indexOf(self.pulseTab), _translate("addSignalDialog", "PULSE"))
from mpl import MplWidget
