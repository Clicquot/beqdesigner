# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'geq.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_geqDialog(object):
    def setupUi(self, geqDialog):
        geqDialog.setObjectName("geqDialog")
        geqDialog.resize(1228, 748)
        self.dialogLayout = QtWidgets.QVBoxLayout(geqDialog)
        self.dialogLayout.setObjectName("dialogLayout")
        self.graphicsLayout = QtWidgets.QHBoxLayout()
        self.graphicsLayout.setObjectName("graphicsLayout")
        self.previewChart = MplWidget(geqDialog)
        self.previewChart.setObjectName("previewChart")
        self.graphicsLayout.addWidget(self.previewChart)
        self.graphControlsLayout = QtWidgets.QVBoxLayout()
        self.graphControlsLayout.setObjectName("graphControlsLayout")
        self.limitsButton = QtWidgets.QToolButton(geqDialog)
        self.limitsButton.setObjectName("limitsButton")
        self.graphControlsLayout.addWidget(self.limitsButton)
        self.showPhase = QtWidgets.QToolButton(geqDialog)
        self.showPhase.setCheckable(True)
        self.showPhase.setObjectName("showPhase")
        self.graphControlsLayout.addWidget(self.showPhase)
        self.showIndividual = QtWidgets.QToolButton(geqDialog)
        self.showIndividual.setCheckable(True)
        self.showIndividual.setObjectName("showIndividual")
        self.graphControlsLayout.addWidget(self.showIndividual)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.graphControlsLayout.addItem(spacerItem)
        self.graphicsLayout.addLayout(self.graphControlsLayout)
        self.dialogLayout.addLayout(self.graphicsLayout)
        self.controlsFrame = QtWidgets.QFrame(geqDialog)
        self.controlsFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.controlsFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.controlsFrame.setObjectName("controlsFrame")
        self.controlsLayout = QtWidgets.QHBoxLayout(self.controlsFrame)
        self.controlsLayout.setObjectName("controlsLayout")
        self.masterControlsLayout = QtWidgets.QGridLayout()
        self.masterControlsLayout.setObjectName("masterControlsLayout")
        self.peqCountLabel = QtWidgets.QLabel(self.controlsFrame)
        self.peqCountLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.peqCountLabel.setObjectName("peqCountLabel")
        self.masterControlsLayout.addWidget(self.peqCountLabel, 0, 0, 1, 1)
        self.channelList = QtWidgets.QListWidget(self.controlsFrame)
        self.channelList.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.channelList.setObjectName("channelList")
        self.masterControlsLayout.addWidget(self.channelList, 1, 0, 1, 4)
        self.advancedMode = QtWidgets.QToolButton(self.controlsFrame)
        self.advancedMode.setCheckable(True)
        self.advancedMode.setChecked(True)
        self.advancedMode.setObjectName("advancedMode")
        self.masterControlsLayout.addWidget(self.advancedMode, 0, 3, 1, 1)
        self.peqCount = QtWidgets.QSpinBox(self.controlsFrame)
        self.peqCount.setMinimum(1)
        self.peqCount.setMaximum(24)
        self.peqCount.setProperty("value", 8)
        self.peqCount.setObjectName("peqCount")
        self.masterControlsLayout.addWidget(self.peqCount, 0, 1, 1, 1)
        self.presetSelector = QtWidgets.QComboBox(self.controlsFrame)
        self.presetSelector.setObjectName("presetSelector")
        self.masterControlsLayout.addWidget(self.presetSelector, 0, 2, 1, 1)
        self.controlsLayout.addLayout(self.masterControlsLayout)
        self.peqScrollArea = QtWidgets.QScrollArea(self.controlsFrame)
        self.peqScrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.peqScrollArea.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.peqScrollArea.setWidgetResizable(True)
        self.peqScrollArea.setObjectName("peqScrollArea")
        self.scrollable = QtWidgets.QWidget()
        self.scrollable.setGeometry(QtCore.QRect(0, 0, 932, 325))
        self.scrollable.setObjectName("scrollable")
        self.scrollableLayout = QtWidgets.QHBoxLayout(self.scrollable)
        self.scrollableLayout.setObjectName("scrollableLayout")
        self.peqScrollArea.setWidget(self.scrollable)
        self.controlsLayout.addWidget(self.peqScrollArea)
        self.dialogLayout.addWidget(self.controlsFrame)
        self.buttonBox = QtWidgets.QDialogButtonBox(geqDialog)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Save)
        self.buttonBox.setObjectName("buttonBox")
        self.dialogLayout.addWidget(self.buttonBox)
        self.dialogLayout.setStretch(0, 1)
        self.dialogLayout.setStretch(1, 1)

        self.retranslateUi(geqDialog)
        self.limitsButton.clicked.connect(geqDialog.show_limits) # type: ignore
        self.peqCount.valueChanged['int'].connect(geqDialog.update_peq_editors) # type: ignore
        self.presetSelector.currentTextChanged['QString'].connect(geqDialog.update_peq_editors) # type: ignore
        self.advancedMode.toggled['bool'].connect(geqDialog.update_peq_editors) # type: ignore
        self.buttonBox.accepted.connect(geqDialog.accept) # type: ignore
        self.buttonBox.rejected.connect(geqDialog.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(geqDialog)

    def retranslateUi(self, geqDialog):
        _translate = QtCore.QCoreApplication.translate
        geqDialog.setWindowTitle(_translate("geqDialog", "EQ Editor"))
        self.showPhase.setText(_translate("geqDialog", "..."))
        self.showIndividual.setText(_translate("geqDialog", "..."))
        self.peqCountLabel.setText(_translate("geqDialog", "Filters"))
        self.advancedMode.setText(_translate("geqDialog", "..."))
from mpl import MplWidget
