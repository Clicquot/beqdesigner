# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'extract.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_extractAudioDialog(object):
    def setupUi(self, extractAudioDialog):
        extractAudioDialog.setObjectName("extractAudioDialog")
        extractAudioDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        extractAudioDialog.resize(880, 794)
        extractAudioDialog.setSizeGripEnabled(True)
        extractAudioDialog.setModal(False)
        self.boxLayout = QtWidgets.QVBoxLayout(extractAudioDialog)
        self.boxLayout.setObjectName("boxLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.inputFilePicker = QtWidgets.QToolButton(extractAudioDialog)
        self.inputFilePicker.setObjectName("inputFilePicker")
        self.gridLayout.addWidget(self.inputFilePicker, 0, 2, 1, 1)
        self.outputFilename = QtWidgets.QLineEdit(extractAudioDialog)
        self.outputFilename.setObjectName("outputFilename")
        self.gridLayout.addWidget(self.outputFilename, 7, 1, 1, 1)
        self.streamsLabel = QtWidgets.QLabel(extractAudioDialog)
        self.streamsLabel.setObjectName("streamsLabel")
        self.gridLayout.addWidget(self.streamsLabel, 1, 0, 1, 1)
        self.inputFileLabel = QtWidgets.QLabel(extractAudioDialog)
        self.inputFileLabel.setObjectName("inputFileLabel")
        self.gridLayout.addWidget(self.inputFileLabel, 0, 0, 1, 1)
        self.ffmpegOutput = QtWidgets.QPlainTextEdit(extractAudioDialog)
        self.ffmpegOutput.setEnabled(True)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        self.ffmpegOutput.setFont(font)
        self.ffmpegOutput.setReadOnly(True)
        self.ffmpegOutput.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.ffmpegOutput.setObjectName("ffmpegOutput")
        self.gridLayout.addWidget(self.ffmpegOutput, 9, 1, 1, 1)
        self.targetDirPicker = QtWidgets.QToolButton(extractAudioDialog)
        self.targetDirPicker.setObjectName("targetDirPicker")
        self.gridLayout.addWidget(self.targetDirPicker, 6, 2, 1, 1)
        self.showProbeButton = QtWidgets.QToolButton(extractAudioDialog)
        self.showProbeButton.setObjectName("showProbeButton")
        self.gridLayout.addWidget(self.showProbeButton, 1, 2, 1, 1)
        self.monoMix = QtWidgets.QCheckBox(extractAudioDialog)
        self.monoMix.setEnabled(True)
        self.monoMix.setChecked(True)
        self.monoMix.setObjectName("monoMix")
        self.gridLayout.addWidget(self.monoMix, 5, 1, 1, 1)
        self.targetDir = QtWidgets.QLineEdit(extractAudioDialog)
        self.targetDir.setEnabled(False)
        self.targetDir.setObjectName("targetDir")
        self.gridLayout.addWidget(self.targetDir, 6, 1, 1, 1)
        self.outputFilenameLabel = QtWidgets.QLabel(extractAudioDialog)
        self.outputFilenameLabel.setObjectName("outputFilenameLabel")
        self.gridLayout.addWidget(self.outputFilenameLabel, 7, 0, 1, 1)
        self.ffmpegCommandLine = QtWidgets.QPlainTextEdit(extractAudioDialog)
        self.ffmpegCommandLine.setEnabled(True)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        self.ffmpegCommandLine.setFont(font)
        self.ffmpegCommandLine.setReadOnly(True)
        self.ffmpegCommandLine.setObjectName("ffmpegCommandLine")
        self.gridLayout.addWidget(self.ffmpegCommandLine, 8, 1, 1, 1)
        self.ffmpegOutputLabel = QtWidgets.QLabel(extractAudioDialog)
        self.ffmpegOutputLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.ffmpegOutputLabel.setObjectName("ffmpegOutputLabel")
        self.gridLayout.addWidget(self.ffmpegOutputLabel, 9, 0, 1, 1)
        self.ffmpegCommandLabel = QtWidgets.QLabel(extractAudioDialog)
        self.ffmpegCommandLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.ffmpegCommandLabel.setObjectName("ffmpegCommandLabel")
        self.gridLayout.addWidget(self.ffmpegCommandLabel, 8, 0, 1, 1)
        self.targetDirectoryLabel = QtWidgets.QLabel(extractAudioDialog)
        self.targetDirectoryLabel.setObjectName("targetDirectoryLabel")
        self.gridLayout.addWidget(self.targetDirectoryLabel, 6, 0, 1, 1)
        self.inputFile = QtWidgets.QLineEdit(extractAudioDialog)
        self.inputFile.setEnabled(False)
        self.inputFile.setObjectName("inputFile")
        self.gridLayout.addWidget(self.inputFile, 0, 1, 1, 1)
        self.audioStreams = QtWidgets.QComboBox(extractAudioDialog)
        self.audioStreams.setObjectName("audioStreams")
        self.gridLayout.addWidget(self.audioStreams, 1, 1, 1, 1)
        self.lfeChannelIndexLabel = QtWidgets.QLabel(extractAudioDialog)
        self.lfeChannelIndexLabel.setObjectName("lfeChannelIndexLabel")
        self.gridLayout.addWidget(self.lfeChannelIndexLabel, 4, 0, 1, 1)
        self.channelCount = QtWidgets.QSpinBox(extractAudioDialog)
        self.channelCount.setMinimum(1)
        self.channelCount.setObjectName("channelCount")
        self.gridLayout.addWidget(self.channelCount, 3, 1, 1, 1)
        self.channelCountLabel = QtWidgets.QLabel(extractAudioDialog)
        self.channelCountLabel.setObjectName("channelCountLabel")
        self.gridLayout.addWidget(self.channelCountLabel, 3, 0, 1, 1)
        self.lfeChannelIndex = QtWidgets.QSpinBox(extractAudioDialog)
        self.lfeChannelIndex.setMinimum(0)
        self.lfeChannelIndex.setObjectName("lfeChannelIndex")
        self.gridLayout.addWidget(self.lfeChannelIndex, 4, 1, 1, 1)
        self.gridLayout.setRowStretch(0, 1)
        self.boxLayout.addLayout(self.gridLayout)
        self.buttonLayout = QtWidgets.QGridLayout()
        self.buttonLayout.setObjectName("buttonLayout")
        self.buttonBox = QtWidgets.QDialogButtonBox(extractAudioDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonLayout.addWidget(self.buttonBox, 0, 0, 1, 1)
        self.boxLayout.addLayout(self.buttonLayout)

        self.retranslateUi(extractAudioDialog)
        self.buttonBox.accepted.connect(extractAudioDialog.accept)
        self.buttonBox.rejected.connect(extractAudioDialog.reject)
        self.inputFilePicker.clicked.connect(extractAudioDialog.selectFile)
        self.showProbeButton.clicked.connect(extractAudioDialog.showProbeInDetail)
        self.targetDirPicker.clicked.connect(extractAudioDialog.setTargetDirectory)
        self.outputFilename.editingFinished.connect(extractAudioDialog.updateFfmpegCommand)
        self.audioStreams.currentIndexChanged['int'].connect(extractAudioDialog.updateFfmpegSpec)
        self.outputFilename.editingFinished.connect(extractAudioDialog.updateFfmpegCommand)
        self.monoMix.clicked.connect(extractAudioDialog.toggleMonoMix)
        self.lfeChannelIndex.valueChanged['int'].connect(extractAudioDialog.overrideFfmpegSpec)
        self.channelCount.valueChanged['int'].connect(extractAudioDialog.overrideFfmpegSpec)
        QtCore.QMetaObject.connectSlotsByName(extractAudioDialog)

    def retranslateUi(self, extractAudioDialog):
        _translate = QtCore.QCoreApplication.translate
        extractAudioDialog.setWindowTitle(_translate("extractAudioDialog", "Extract Audio"))
        self.inputFilePicker.setText(_translate("extractAudioDialog", "..."))
        self.streamsLabel.setText(_translate("extractAudioDialog", "Streams"))
        self.inputFileLabel.setText(_translate("extractAudioDialog", "File"))
        self.targetDirPicker.setText(_translate("extractAudioDialog", "..."))
        self.showProbeButton.setText(_translate("extractAudioDialog", "..."))
        self.monoMix.setText(_translate("extractAudioDialog", "Mix to Mono?"))
        self.outputFilenameLabel.setText(_translate("extractAudioDialog", "Output Filename"))
        self.ffmpegOutputLabel.setText(_translate("extractAudioDialog", "ffmpeg output"))
        self.ffmpegCommandLabel.setText(_translate("extractAudioDialog", "ffmpeg command "))
        self.targetDirectoryLabel.setText(_translate("extractAudioDialog", "Target Directory"))
        self.lfeChannelIndexLabel.setText(_translate("extractAudioDialog", "LFE Channel"))
        self.channelCountLabel.setText(_translate("extractAudioDialog", "Channel Count"))
        self.lfeChannelIndex.setToolTip(_translate("extractAudioDialog", "0 = No LFE"))

