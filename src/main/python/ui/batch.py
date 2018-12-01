# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'batch.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_batchExtractDialog(object):
    def setupUi(self, batchExtractDialog):
        batchExtractDialog.setObjectName("batchExtractDialog")
        batchExtractDialog.resize(1727, 925)
        self.verticalLayout = QtWidgets.QVBoxLayout(batchExtractDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.controlFrame = QtWidgets.QFrame(batchExtractDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.controlFrame.sizePolicy().hasHeightForWidth())
        self.controlFrame.setSizePolicy(sizePolicy)
        self.controlFrame.setFrameShape(QtWidgets.QFrame.Panel)
        self.controlFrame.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.controlFrame.setObjectName("controlFrame")
        self.gridLayout = QtWidgets.QGridLayout(self.controlFrame)
        self.gridLayout.setObjectName("gridLayout")
        self.controlsLayout = QtWidgets.QGridLayout()
        self.controlsLayout.setObjectName("controlsLayout")
        self.threads = QtWidgets.QSpinBox(self.controlFrame)
        self.threads.setMinimum(1)
        self.threads.setMaximum(64)
        self.threads.setProperty("value", 1)
        self.threads.setObjectName("threads")
        self.controlsLayout.addWidget(self.threads, 3, 1, 1, 1)
        self.searchButton = QtWidgets.QPushButton(self.controlFrame)
        self.searchButton.setEnabled(False)
        self.searchButton.setObjectName("searchButton")
        self.controlsLayout.addWidget(self.searchButton, 5, 1, 1, 1)
        self.outputDirLabel = QtWidgets.QLabel(self.controlFrame)
        self.outputDirLabel.setObjectName("outputDirLabel")
        self.controlsLayout.addWidget(self.outputDirLabel, 1, 0, 1, 1)
        self.threadsLabel = QtWidgets.QLabel(self.controlFrame)
        self.threadsLabel.setObjectName("threadsLabel")
        self.controlsLayout.addWidget(self.threadsLabel, 3, 0, 1, 1)
        self.filterLabel = QtWidgets.QLabel(self.controlFrame)
        self.filterLabel.setToolTip("")
        self.filterLabel.setObjectName("filterLabel")
        self.controlsLayout.addWidget(self.filterLabel, 0, 0, 1, 1)
        self.extractButton = QtWidgets.QPushButton(self.controlFrame)
        self.extractButton.setEnabled(False)
        self.extractButton.setObjectName("extractButton")
        self.controlsLayout.addWidget(self.extractButton, 5, 2, 1, 1)
        self.resetButton = QtWidgets.QPushButton(self.controlFrame)
        self.resetButton.setEnabled(False)
        self.resetButton.setObjectName("resetButton")
        self.controlsLayout.addWidget(self.resetButton, 5, 3, 1, 1)
        self.outputDirPicker = QtWidgets.QToolButton(self.controlFrame)
        self.outputDirPicker.setObjectName("outputDirPicker")
        self.controlsLayout.addWidget(self.outputDirPicker, 1, 4, 1, 1)
        self.outputDir = QtWidgets.QLineEdit(self.controlFrame)
        self.outputDir.setEnabled(False)
        self.outputDir.setObjectName("outputDir")
        self.controlsLayout.addWidget(self.outputDir, 1, 1, 1, 3)
        self.filter = QtWidgets.QLineEdit(self.controlFrame)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        self.filter.setFont(font)
        self.filter.setText("")
        self.filter.setObjectName("filter")
        self.controlsLayout.addWidget(self.filter, 0, 1, 1, 3)
        self.monoMix = QtWidgets.QCheckBox(self.controlFrame)
        self.monoMix.setChecked(True)
        self.monoMix.setObjectName("monoMix")
        self.controlsLayout.addWidget(self.monoMix, 5, 0, 1, 1)
        self.controlsLayout.setColumnStretch(1, 1)
        self.controlsLayout.setColumnStretch(2, 1)
        self.controlsLayout.setColumnStretch(3, 1)
        self.gridLayout.addLayout(self.controlsLayout, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.controlFrame)
        self.resultsFrame = QtWidgets.QFrame(batchExtractDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.resultsFrame.sizePolicy().hasHeightForWidth())
        self.resultsFrame.setSizePolicy(sizePolicy)
        self.resultsFrame.setFrameShape(QtWidgets.QFrame.Box)
        self.resultsFrame.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.resultsFrame.setObjectName("resultsFrame")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.resultsFrame)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.resultsTitle = QtWidgets.QLabel(self.resultsFrame)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.resultsTitle.setFont(font)
        self.resultsTitle.setFrameShape(QtWidgets.QFrame.Box)
        self.resultsTitle.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.resultsTitle.setAlignment(QtCore.Qt.AlignCenter)
        self.resultsTitle.setObjectName("resultsTitle")
        self.gridLayout_2.addWidget(self.resultsTitle, 0, 0, 1, 1)
        self.resultsScrollArea = QtWidgets.QScrollArea(self.resultsFrame)
        self.resultsScrollArea.setWidgetResizable(True)
        self.resultsScrollArea.setObjectName("resultsScrollArea")
        self.resultsScrollAreaContents = QtWidgets.QWidget()
        self.resultsScrollAreaContents.setGeometry(QtCore.QRect(0, 0, 1669, 660))
        self.resultsScrollAreaContents.setObjectName("resultsScrollAreaContents")
        self.resultsScrollLayout = QtWidgets.QGridLayout(self.resultsScrollAreaContents)
        self.resultsScrollLayout.setObjectName("resultsScrollLayout")
        self.resultsLayout = QtWidgets.QGridLayout()
        self.resultsLayout.setObjectName("resultsLayout")
        self.statusHeaderLabel = QtWidgets.QLabel(self.resultsScrollAreaContents)
        font = QtGui.QFont()
        font.setUnderline(True)
        self.statusHeaderLabel.setFont(font)
        self.statusHeaderLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.statusHeaderLabel.setObjectName("statusHeaderLabel")
        self.resultsLayout.addWidget(self.statusHeaderLabel, 0, 0, 1, 1)
        self.probeHeaderLabel = QtWidgets.QLabel(self.resultsScrollAreaContents)
        font = QtGui.QFont()
        font.setItalic(True)
        font.setUnderline(True)
        self.probeHeaderLabel.setFont(font)
        self.probeHeaderLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.probeHeaderLabel.setObjectName("probeHeaderLabel")
        self.resultsLayout.addWidget(self.probeHeaderLabel, 0, 2, 1, 1)
        self.streamHeaderLabel = QtWidgets.QLabel(self.resultsScrollAreaContents)
        font = QtGui.QFont()
        font.setBold(False)
        font.setItalic(True)
        font.setUnderline(True)
        font.setWeight(50)
        self.streamHeaderLabel.setFont(font)
        self.streamHeaderLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.streamHeaderLabel.setObjectName("streamHeaderLabel")
        self.resultsLayout.addWidget(self.streamHeaderLabel, 0, 3, 1, 1)
        self.inputFileHeaderLabel = QtWidgets.QLabel(self.resultsScrollAreaContents)
        font = QtGui.QFont()
        font.setBold(False)
        font.setItalic(True)
        font.setUnderline(True)
        font.setWeight(50)
        self.inputFileHeaderLabel.setFont(font)
        self.inputFileHeaderLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.inputFileHeaderLabel.setObjectName("inputFileHeaderLabel")
        self.resultsLayout.addWidget(self.inputFileHeaderLabel, 0, 1, 1, 1)
        self.channelsHeaderLabel = QtWidgets.QLabel(self.resultsScrollAreaContents)
        font = QtGui.QFont()
        font.setBold(False)
        font.setItalic(True)
        font.setUnderline(True)
        font.setWeight(50)
        self.channelsHeaderLabel.setFont(font)
        self.channelsHeaderLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.channelsHeaderLabel.setObjectName("channelsHeaderLabel")
        self.resultsLayout.addWidget(self.channelsHeaderLabel, 0, 4, 1, 1)
        self.outputFileHeaderLabel = QtWidgets.QLabel(self.resultsScrollAreaContents)
        font = QtGui.QFont()
        font.setBold(False)
        font.setItalic(True)
        font.setUnderline(True)
        font.setWeight(50)
        self.outputFileHeaderLabel.setFont(font)
        self.outputFileHeaderLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.outputFileHeaderLabel.setObjectName("outputFileHeaderLabel")
        self.resultsLayout.addWidget(self.outputFileHeaderLabel, 0, 6, 1, 1)
        self.progressHeaderLabel = QtWidgets.QLabel(self.resultsScrollAreaContents)
        font = QtGui.QFont()
        font.setBold(False)
        font.setItalic(True)
        font.setUnderline(True)
        font.setWeight(50)
        self.progressHeaderLabel.setFont(font)
        self.progressHeaderLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.progressHeaderLabel.setObjectName("progressHeaderLabel")
        self.resultsLayout.addWidget(self.progressHeaderLabel, 0, 8, 1, 1)
        self.lfeHeaderLabel = QtWidgets.QLabel(self.resultsScrollAreaContents)
        font = QtGui.QFont()
        font.setBold(False)
        font.setItalic(True)
        font.setUnderline(True)
        font.setWeight(50)
        self.lfeHeaderLabel.setFont(font)
        self.lfeHeaderLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.lfeHeaderLabel.setObjectName("lfeHeaderLabel")
        self.resultsLayout.addWidget(self.lfeHeaderLabel, 0, 5, 1, 1)
        self.ffmpegCliLabel = QtWidgets.QLabel(self.resultsScrollAreaContents)
        font = QtGui.QFont()
        font.setItalic(True)
        font.setUnderline(True)
        self.ffmpegCliLabel.setFont(font)
        self.ffmpegCliLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.ffmpegCliLabel.setObjectName("ffmpegCliLabel")
        self.resultsLayout.addWidget(self.ffmpegCliLabel, 0, 7, 1, 1)
        self.resultsLayout.setColumnStretch(1, 1)
        self.resultsLayout.setColumnStretch(3, 2)
        self.resultsLayout.setColumnStretch(6, 1)
        self.resultsLayout.setColumnStretch(8, 1)
        self.resultsScrollLayout.addLayout(self.resultsLayout, 0, 0, 1, 1)
        self.resultsScrollArea.setWidget(self.resultsScrollAreaContents)
        self.gridLayout_2.addWidget(self.resultsScrollArea, 1, 0, 1, 1)
        self.verticalLayout.addWidget(self.resultsFrame)

        self.retranslateUi(batchExtractDialog)
        self.searchButton.clicked.connect(batchExtractDialog.search)
        self.extractButton.clicked.connect(batchExtractDialog.extract)
        self.outputDirPicker.clicked.connect(batchExtractDialog.select_output)
        self.filter.textChanged['QString'].connect(batchExtractDialog.enable_search)
        self.resetButton.clicked.connect(batchExtractDialog.reset_batch)
        self.threads.valueChanged['int'].connect(batchExtractDialog.change_pool_size)
        QtCore.QMetaObject.connectSlotsByName(batchExtractDialog)

    def retranslateUi(self, batchExtractDialog):
        _translate = QtCore.QCoreApplication.translate
        batchExtractDialog.setWindowTitle(_translate("batchExtractDialog", "Extract Audio"))
        self.searchButton.setText(_translate("batchExtractDialog", "Search"))
        self.outputDirLabel.setText(_translate("batchExtractDialog", "Output Directory"))
        self.threadsLabel.setText(_translate("batchExtractDialog", "Threads"))
        self.filterLabel.setText(_translate("batchExtractDialog", "Search Filter"))
        self.extractButton.setText(_translate("batchExtractDialog", "Extract"))
        self.resetButton.setText(_translate("batchExtractDialog", "Reset"))
        self.outputDirPicker.setText(_translate("batchExtractDialog", "..."))
        self.filter.setPlaceholderText(_translate("batchExtractDialog", "Enter 1 or more search filters, e.g. w:/films/*.mkv;y:/videos/**/*.m2ts"))
        self.monoMix.setText(_translate("batchExtractDialog", "Mix to Mono?"))
        self.resultsTitle.setText(_translate("batchExtractDialog", "Results"))
        self.statusHeaderLabel.setText(_translate("batchExtractDialog", "Status"))
        self.probeHeaderLabel.setText(_translate("batchExtractDialog", "Probe"))
        self.streamHeaderLabel.setText(_translate("batchExtractDialog", "Stream"))
        self.inputFileHeaderLabel.setText(_translate("batchExtractDialog", "Input File"))
        self.channelsHeaderLabel.setText(_translate("batchExtractDialog", "Channels"))
        self.outputFileHeaderLabel.setText(_translate("batchExtractDialog", "Output File"))
        self.progressHeaderLabel.setText(_translate("batchExtractDialog", "Progress"))
        self.lfeHeaderLabel.setText(_translate("batchExtractDialog", "LFE"))
        self.ffmpegCliLabel.setText(_translate("batchExtractDialog", "ffmpeg"))

