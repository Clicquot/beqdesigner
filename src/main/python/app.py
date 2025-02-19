import gzip
import json
import logging
import os
import re
from collections import abc
from contextlib import contextmanager

import math
import matplotlib
import sys
from scipy import signal

matplotlib.use("Qt5Agg")
os.environ['QT_API'] = 'pyqt5'
# os.environ['PYQTGRAPH_QT_LIB'] = 'PyQt5'

from model.waveform import WaveformController
from model.checker import VersionChecker, ReleaseNotesDialog
from model.report import SaveReportDialog, block_signals
from model.preferences import DISPLAY_SHOW_FILTERED_SIGNALS, SYSTEM_CHECK_FOR_UPDATES, BIQUAD_EXPORT_MAX, \
    BIQUAD_EXPORT_FS, BIQUAD_EXPORT_DEVICE, SHOW_NO_FILTERS, SYSTEM_CHECK_FOR_BETA_UPDATES, \
    BEQ_REPOS, BEQ_DEFAULT_REPO, BEQ_REPOS_2

from ui.delegates import RegexValidator

import pyqtgraph as pg
import qtawesome as qta
from matplotlib import style

from model.iir import Passthrough, CompleteFilter, as_equalizer_apo, COMBINED
from ui.biquad import Ui_exportBiquadDialog
from ui.savechart import Ui_saveChartDialog

from qtpy import QtCore, QtWidgets
from qtpy.QtCore import QSettings, QThreadPool, QUrl
from qtpy.QtGui import QIcon, QFont, QCursor, QTextCursor, QDesktopServices
from qtpy.QtWidgets import QMainWindow, QApplication, QErrorMessage, QAbstractItemView, QDialog, QFileDialog, \
    QHeaderView, QMessageBox, QHBoxLayout, QToolButton

from model.preferences import PreferencesDialog, BINARIES_GROUP, ANALYSIS_TARGET_FS, STYLE_MATPLOTLIB_THEME, \
    Preferences, STYLE_MATPLOTLIB_THEME_DEFAULT, SCREEN_GEOMETRY, SCREEN_WINDOW_STATE, FILTERS_PRESET_x, \
    DISPLAY_SHOW_LEGEND, DISPLAY_SHOW_FILTERS, SHOW_FILTER_OPTIONS, SHOW_SIGNAL_OPTIONS, DISPLAY_SHOW_SIGNALS, \
    SHOW_FILTERED_SIGNAL_OPTIONS
from ui.beq import Ui_MainWindow

logger = logging.getLogger('beq')
logging.getLogger('matplotlib').setLevel(logging.WARNING)


@contextmanager
def wait_cursor(msg=None):
    '''
    Allows long running functions to show a busy cursor.
    :param msg: a message to put in the status bar.
    '''
    try:
        QApplication.setOverrideCursor(QCursor(QtCore.Qt.WaitCursor))
        yield
    finally:
        QApplication.restoreOverrideCursor()


class BeqDesigner(QMainWindow, Ui_MainWindow):
    '''
    The main UI.
    '''

    def __init__(self, app, prefs, parent=None):
        super(BeqDesigner, self).__init__(parent)
        self.logger = logging.getLogger('beqdesigner')
        self.app = app
        self.preferences = prefs
        if getattr(sys, 'frozen', False):
            self.__style_path_root = sys._MEIPASS
        else:
            self.__style_path_root = os.path.dirname(__file__)
        self.__version = '0.0.0-alpha.1'
        v_path = os.path.abspath(os.path.join(self.__style_path_root, 'VERSION'))
        try:
            with open(v_path) as version_file:
                self.__version = version_file.read().strip()
        except:
            logger.exception(f"Unable to read {v_path}")
        if self.preferences.get(SYSTEM_CHECK_FOR_UPDATES):
            QThreadPool.globalInstance().start(VersionChecker(self.preferences.get(SYSTEM_CHECK_FOR_BETA_UPDATES),
                                                              self.__alert_on_old_version,
                                                              self.__alert_on_version_check_fail,
                                                              self.__version))

        matplotlib_theme = self.preferences.get(STYLE_MATPLOTLIB_THEME)
        if matplotlib_theme is not None:
            if matplotlib_theme.startswith('beq'):
                style.use(os.path.join(self.__style_path_root, 'style', 'mpl', f"{matplotlib_theme}.mplstyle"))
            else:
                style.use(matplotlib_theme)

        pg.setConfigOption('background', matplotlib.colors.to_hex(matplotlib.rcParams['axes.facecolor']))
        pg.setConfigOption('foreground', matplotlib.colors.to_hex(matplotlib.rcParams['axes.edgecolor']))
        pg.setConfigOption('leftButtonPan', False)
        self.setupUi(self)
        self.__decorate_splitter()
        self.limitsButton.setIcon(qta.icon('fa5s.arrows-alt'))
        self.showValuesButton.setIcon(qta.icon('ei.eye-open'))
        # init beq repos for 0.9.0 backwards compatibility
        self.__ensure_beq_repos_exist()
        # logs
        from model.log import RollingLogger
        self.logViewer = RollingLogger(self.preferences, parent=self)
        self.actionShow_Logs.triggered.connect(self.logViewer.show_logs)
        self.actionPreferences.triggered.connect(self.showPreferences)
        # init a default signal for when we want to edit a filter without a signal
        from model.signal import SingleChannelSignalData, Signal
        default_fs = self.preferences.get(ANALYSIS_TARGET_FS)
        default_signal = Signal('default', signal.unit_impulse(default_fs, 'mid'), self.preferences, fs=default_fs)
        self.__default_signal = SingleChannelSignalData(name='default',
                                                        signal=default_signal,
                                                        filter=CompleteFilter(fs=default_fs))
        # init the filter view selector
        self.showFilters.blockSignals(True)
        for x in SHOW_FILTER_OPTIONS:
            self.showFilters.addItem(x)
        selected = self.preferences.get(DISPLAY_SHOW_FILTERS)
        selected_idx = self.showFilters.findText(selected)
        if selected_idx != -1:
            self.showFilters.setCurrentIndex(selected_idx)
        else:
            logger.info(f"Ignoring unknown cached preference for {DISPLAY_SHOW_FILTERS} - {selected}")
        self.showFilters.blockSignals(False)
        # filter view/model
        self.actionShow_Filter_Widget.triggered.connect(lambda:self.editFilter(small=True))
        self.filterView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.filterView.doubleClicked.connect(self.editFilter)
        from model.filter import FilterTableModel, FilterModel
        self.__filter_model = FilterModel(self.filterView, self.preferences, label=self.filtersLabel,
                                          on_update=self.on_filter_change)
        self.__filter_table_model = FilterTableModel(self.__filter_model, parent=parent)
        self.filterView.setModel(self.__filter_table_model)
        self.filterView.selectionModel().selectionChanged.connect(self.on_filter_selected)
        self.filterView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        for i in range(1, 4):
            getattr(self, f"action_load_preset_{i}").triggered.connect(self.load_preset(i))
            getattr(self, f"action_clear_preset_{i}").triggered.connect(self.clear_preset(i))
            getattr(self, f"action_store_preset_{i}").triggered.connect(self.set_preset(i))
            self.enable_preset(i)
        self.actionAdd_BEQ_Filter.triggered.connect(self.add_beq_filter)
        self.actionClear_Filters.triggered.connect(self.clearFilters)
        # init the signal view selector
        self.showSignals.blockSignals(True)
        for x in SHOW_SIGNAL_OPTIONS:
            self.showSignals.addItem(x)
        selected = self.preferences.get(DISPLAY_SHOW_SIGNALS)
        selected_idx = self.showSignals.findText(selected)
        if selected_idx != -1:
            self.showSignals.setCurrentIndex(selected_idx)
        else:
            logger.info(f"Ignoring unknown cached preference for {DISPLAY_SHOW_SIGNALS} - {selected}")
        self.showSignals.blockSignals(False)
        # init the filtered signal view selecter
        self.showFilteredSignals.blockSignals(True)
        for x in SHOW_FILTERED_SIGNAL_OPTIONS:
            self.showFilteredSignals.addItem(x)
        selected = self.preferences.get(DISPLAY_SHOW_FILTERED_SIGNALS)
        selected_idx = self.showFilteredSignals.findText(selected)
        if selected_idx != -1:
            self.showFilteredSignals.setCurrentIndex(selected_idx)
        else:
            logger.info(f"Ignoring unknown cached preference for {DISPLAY_SHOW_FILTERED_SIGNALS} - {selected}")
        self.showFilteredSignals.blockSignals(False)
        # signal model
        self.__cached_selected_signal = None
        self.__configure_signal_model(parent)
        # signal editor
        self.actionMerge_Signals.triggered.connect(self.__open_merge_signal_dialog)
        self.actionMerge_Signals.setEnabled(False)
        # magnitude
        self.showLegend.setChecked(bool(self.preferences.get(DISPLAY_SHOW_LEGEND)))
        from model.magnitude import MagnitudeModel
        self.__magnitude_model = MagnitudeModel('main', self.mainChart, self.preferences,
                                                self.__signal_model.get_curve_data, 'Signals',
                                                secondary_data_provider=self.__filter_model.get_curve_data,
                                                secondary_name='Filters',
                                                show_legend=lambda: self.showLegend.isChecked(), allow_line_resize=True)
        self.__filter_model.filter = self.__default_signal.filter
        self.y1MaxPlus10Button.setIcon(qta.icon('mdi.chevron-double-up'))
        self.y1MaxPlus5Button.setIcon(qta.icon('mdi.chevron-up'))
        self.y1MaxMinus5Button.setIcon(qta.icon('mdi.chevron-down'))
        self.y1MaxMinus10Button.setIcon(qta.icon('mdi.chevron-double-down'))
        self.y1MinPlus10Button.setIcon(qta.icon('mdi.chevron-double-up'))
        self.y1MinPlus5Button.setIcon(qta.icon('mdi.chevron-up'))
        self.y1MinMinus5Button.setIcon(qta.icon('mdi.chevron-down'))
        self.y1MinMinus10Button.setIcon(qta.icon('mdi.chevron-double-down'))
        self.y1AutoOnButton.setIcon(qta.icon('fa5s.magic'))
        self.y1AutoOnButton.setChecked(True)
        self.y1AutoOffButton.setIcon(qta.icon('fa5s.magic', 'fa5s.ban', options=[{'scale_factor': 0.75}, {}]))
        self.y2MaxPlus10Button.setIcon(qta.icon('mdi.chevron-double-up'))
        self.y2MaxPlus5Button.setIcon(qta.icon('mdi.chevron-up'))
        self.y2MaxMinus5Button.setIcon(qta.icon('mdi.chevron-down'))
        self.y2MaxMinus10Button.setIcon(qta.icon('mdi.chevron-double-down'))
        self.y2MinPlus10Button.setIcon(qta.icon('mdi.chevron-double-up'))
        self.y2MinPlus5Button.setIcon(qta.icon('mdi.chevron-up'))
        self.y2MinMinus5Button.setIcon(qta.icon('mdi.chevron-down'))
        self.y2MinMinus10Button.setIcon(qta.icon('mdi.chevron-double-down'))
        self.y2AutoOnButton.setIcon(qta.icon('fa5s.magic'))
        self.y2AutoOnButton.setChecked(True)
        self.y2AutoOffButton.setIcon(qta.icon('fa5s.magic', 'fa5s.ban', options=[{'scale_factor': 0.75}, {}]))
        # waveform
        self.__waveform_controller = WaveformController(self.preferences,
                                                        self.__signal_model,
                                                        self.waveformChart,
                                                        self.filteredSpectrumChart,
                                                        self.signalSelector,
                                                        self.rmsLevel,
                                                        self.headroom,
                                                        self.crestFactor,
                                                        self.bmHeadroom,
                                                        self.bmlpfPosition,
                                                        self.bmClipBefore,
                                                        self.bmClipAfter,
                                                        self.waveformIsFiltered,
                                                        self.hardClipWaveform,
                                                        self.startTime,
                                                        self.endTime,
                                                        self.showSpectrumButton,
                                                        self.hideSpectrumButton,
                                                        self.zoomInButton,
                                                        self.zoomOutButton,
                                                        self.compareSpectrumButton,
                                                        self.sourceFile,
                                                        self.loadSignalButton,
                                                        self.filteredSpectrumLimitsButton,
                                                        self.showStatsButton,
                                                        self.yMin,
                                                        self.yMax,
                                                        self.bmhpfOn,
                                                        self.saveWaveformChartButton)
        self.__hide_waveform_chart()
        self.actionClear_Signals.triggered.connect(self.clearSignals)
        # processing
        self.ensurePathContainsExternalTools()
        # extraction
        self.actionExtract_Audio.triggered.connect(self.showExtractAudioDialog)
        self.action_Remux_Audio.triggered.connect(self.showRemuxAudioDialog)
        self.action_Batch_Extract.triggered.connect(self.showBatchExtractDialog)
        # analysis
        self.actionAnalyse_Audio.triggered.connect(self.showAnalyseAudioDialog)
        # import
        self.actionLoad_Filter.triggered.connect(self.importFilter)
        self.actionLoad_Signal.triggered.connect(self.importSignal)
        self.action_Load_Project.triggered.connect(self.importProject)
        # export
        self.actionSave_Report.triggered.connect(self.exportReport)
        self.actionSave_Chart.triggered.connect(self.exportChart)
        self.actionExport_Biquad.triggered.connect(self.exportBiquads)
        self.actionSave_Filter.triggered.connect(self.exportFilter)
        self.actionExport_FRD.triggered.connect(self.showExportFRDDialog)
        self.actionSave_Signal.triggered.connect(self.showExportSignalDialog)
        self.action_Save_Project.triggered.connect(self.exportProject)
        self.actionAbout.triggered.connect(self.showAbout)
        # tools
        self.actionMerge_Minidsp_XML.triggered.connect(self.merge_minidsp_xml)
        self.actionCreate_AVS_Post.triggered.connect(self.create_avs_post)
        self.actionUser_Guide.triggered.connect(self.show_help)
        self.actionRelease_Notes.triggered.connect(self.show_release_notes)
        self.actionBrowse_Catalogue.triggered.connect(self.show_catalogue)
        self.actionExport_BEQ_Filter.triggered.connect(self.export_beq_filter)
        self.actionSync_with_HTP_1.triggered.connect(self.sync_htp1)
        self.actionManage_JRiver_MC.triggered.connect(self.__import_jriver_peq)

    def __ensure_beq_repos_exist(self):
        '''
        Allows the user to choose whether to add MOberhardt's BEQ repo.
        This should only ever be displayed once on upgrade beyond 0.9.0
        '''
        if self.preferences.has(BEQ_REPOS):
            repo_list = self.preferences.get(BEQ_REPOS).split('|')
        else:
            repo_list = [BEQ_DEFAULT_REPO]
            result = QMessageBox.question(self,
                                          'Add MOberhardt BEQ Repo?',
                                          f"Do you want to use MOberhardt's BEQs?",
                                          QMessageBox.Yes | QMessageBox.No,
                                          QMessageBox.Yes)
            if result == QMessageBox.Yes:
                repo_list.append('https://github.com/Mobe1969/miniDSPBEQ.git')
        if not self.preferences.has(BEQ_REPOS_2):
            result = QMessageBox.question(self,
                                          'Add halcyon888 BEQ Repo?',
                                          f"Do you want to use halcyons888's BEQs?",
                                          QMessageBox.Yes | QMessageBox.No,
                                          QMessageBox.Yes)
            if result == QMessageBox.Yes:
                repo_list.append('https://github.com/halcyon-888/miniDSPBEQ.git')
        self.preferences.set(BEQ_REPOS, '|'.join({r: '' for r in repo_list}.keys()))
        self.preferences.set(BEQ_REPOS_2, 'Upgraded')

    def show_release_notes(self):
        ''' Shows the release notes '''
        QThreadPool.globalInstance().start(VersionChecker(self.preferences.get(SYSTEM_CHECK_FOR_BETA_UPDATES),
                                                          self.__alert_on_old_version,
                                                          self.__alert_on_version_check_fail,
                                                          self.__version,
                                                          signal_anyway=True))

    def show_help(self):
        ''' Opens the user guide in a browser '''
        QDesktopServices.openUrl(QUrl('https://beqdesigner.readthedocs.io/en/latest'))

    def smoothSignals(self):
        ''' Applies the current smoothing options to the visible signals. '''
        fraction_idx = self.octaveSmoothing.currentIndex()
        if fraction_idx == 0:
            smooth_type = 0
        else:
            try:
                smooth_type = int(self.octaveSmoothing.currentText()[2:])
            except:
                smooth_type = 'SG'
        with wait_cursor():
            if self.smoothAllSignals.isChecked():
                for s in self.__signal_model:
                    s.smooth(smooth_type)
            else:
                signal_select = self.signalView.selectionModel()
                if signal_select.hasSelection() and len(signal_select.selectedRows()) == 1:
                    signal_data = self.__signal_model[signal_select.selectedRows()[0].row()]
                    if signal_data.signal is not None:
                        signal_data.smooth(smooth_type)
        self.__magnitude_model.redraw()
        self.signalView.viewport().update()

    def __decorate_splitter(self):
        '''
        Adds some visible handles to the splitter so we can quickly show/hide it.
        '''
        handle = self.chartSplitter.handle(1)
        self.chartSplitter.setHandleWidth(15)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        button = QToolButton(handle)
        button.setIcon(qta.icon('fa5s.chevron-up'))
        button.clicked.connect(self.__show_waveform_chart)
        layout.addWidget(button)
        button = QToolButton(handle)
        button.setIcon(qta.icon('fa5s.chevron-down'))
        button.clicked.connect(self.__hide_waveform_chart)
        layout.addWidget(button)
        handle.setLayout(layout)

    def __hide_waveform_chart(self):
        self.chartSplitter.setSizes([1, 0])
        self.__waveform_controller.on_visibility_change(show=False)

    def __show_waveform_chart(self):
        self.chartSplitter.setSizes([100000, 100000])
        self.__waveform_controller.on_visibility_change(show=True)

    def __alert_on_version_check_fail(self, message):
        '''
        Displays an alert if the version check fails.
        :param message: the message.
        '''
        msg_box = QMessageBox()
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle('Unable to Complete Version Check')
        msg_box.exec()

    def __alert_on_old_version(self, versions, issues):
        ''' Presents a dialog if there is a new version available. '''
        ReleaseNotesDialog(self, versions, issues).exec()

    def __configure_signal_model(self, parent):
        '''
        Wires up the signal model so that
        * only one row can be selected at a time
        * there is always a row selected
        * the filter model is always honouring the selected row correctly (where correctly means the filter model is
        operating on the filter of the selected signal if it is an unlinked signal or a master OR the filter of the
        master of the selected signal if the signal is a slave).
        This last point is crucial as otherwise the linked signals won't update at the same time.
        '''
        self.signalView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.signalView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.signalView.setSelectionMode(QAbstractItemView.SingleSelection)
        from model.signal import SignalModel, SignalTableModel
        self.__signal_model = SignalModel(self.signalView, self.__default_signal, self.preferences,
                                          on_update=self.on_signal_change)
        self.__signal_table_model = SignalTableModel(self.__signal_model, parent=parent)
        self.signalView.setModel(self.__signal_table_model)
        self.signalView.selectionModel().selectionChanged.connect(self.on_signal_selected)
        self.signalView.model().dataChanged.connect(self.on_signal_data_change)
        self.signalView.model().modelAboutToBeReset.connect(self.on_signal_data_about_to_reset)
        self.signalView.model().modelReset.connect(self.on_signal_data_reset)
        self.signalView.model().rowsInserted.connect(self.__handle_signals_inserted)
        self.signalView.model().rowsRemoved.connect(self.__handle_signals_removed)
        self.signalView.setItemDelegateForColumn(0, RegexValidator('^.+$'))

    def on_signal_data_about_to_reset(self):
        '''
        Caches the selected signal so we can restore it post reset.
        '''
        signal_select = self.signalView.selectionModel()
        if signal_select.hasSelection() and len(signal_select.selectedRows()) == 1:
            self.__cached_selected_signal = self.__signal_model[signal_select.selectedRows()[0].row()]

    def on_signal_data_reset(self):
        '''
        Restores the cached selected signal if we have one.
        '''
        selected_row = -1
        if self.__cached_selected_signal is not None:
            for idx, s in enumerate(self.__signal_model):
                if s.name == self.__cached_selected_signal.name:
                    selected_row = idx
            self.__cached_selected_signal = None
        else:
            signal_count = len(self.__signal_model)
            if signal_count > 0:
                selected_row = signal_count - 1
        if selected_row > -1:
            logger.debug(f"Selected row {selected_row} after signal data reset")
            self.signalView.selectRow(selected_row)

    def on_signal_data_change(self):
        '''
        Delegates to on_signal_change which we can't call directly because of the argument mismatch (dataChanged emits
        the QModelIndexes specifying which data has changed which we don't care about).
        '''
        logger.debug(f"Handling signal data change")
        self.on_signal_selected()
        self.on_signal_change()

    def on_signal_change(self, names=None):
        '''
        Reacts to a change in the signal model by updating the reference and redrawing the chart.
        :param names: the signal names.
        '''
        if names is not None:
            self.update_reference_series(names, self.signalReference, True)
        self.__waveform_controller.refresh_selector()
        if self.signalSelector.count() == 1:
            self.__hide_waveform_chart()
        self.linkSignalButton.setEnabled(len(self.__signal_model) > 1)
        self.__magnitude_model.redraw()
        signal_count = sum(s.signal is not None for s in self.__signal_model.non_bm_signals)
        signal_count += sum([len(bm.channels) for bm in self.__signal_model.bass_managed_signals])
        self.actionMerge_Signals.setEnabled(signal_count > 1)

    def __get_selected_signal(self):
        '''
        :return: the selected signal (as selected in the table going back to its master if the selected signal is a
        slave) or the default signal if nothing is selected.
        '''
        signal_select = self.signalView.selectionModel()
        if signal_select.hasSelection() and len(signal_select.selectedRows()) == 1:
            signal = self.__signal_model[signal_select.selectedRows()[0].row()]
            if signal.master is not None:
                signal = signal.master
        else:
            signal = self.__signal_model.default_signal
        return signal

    def __handle_signals_inserted(self, idx, first, last):
        '''
        Selects the last signal added by default.
        :param idx: the idx.
        :param first: the first row inserted.
        :param last: the last row inserted.
        '''
        logger.debug(f"Selecting signal {last} on insert")
        self.signalView.selectRow(last)

    def __handle_signals_removed(self, idx, first, last):
        '''
        Ensures the correct signal is selected when signals are removed. This defaults to the last signal in the table
        if there are any signals otherwise it reverts to the default signal.
        :param idx: the idx.
        :param first: first row removed.
        :param last: last row removed.
        '''
        signal_count = len(self.__signal_model)
        if signal_count > 0:
            logger.debug(f"Selecting signal {signal_count - 1} on remove")
            self.signalView.selectRow(signal_count - 1)
        else:
            logger.debug(f"No signals in model, selecting default filter on remove")
            self.on_signal_selected()

    def addSignal(self):
        '''
        Adds signals via the signal dialog.
        '''
        from model.signal import SignalDialog
        SignalDialog(self.preferences, self.__signal_model, parent=self).show()

    def linkSignals(self):
        '''
        Lets the user link signals via a matrix mapping.
        '''
        from model.link import LinkSignalsDialog
        LinkSignalsDialog(self.__signal_model, parent=self).exec()

    def deleteSignal(self):
        '''
        Deletes the currently selected signals.
        '''
        selection = self.signalView.selectionModel()
        if selection.hasSelection():
            self.__signal_model.delete([x.row() for x in selection.selectedRows()])
        if len(self.__signal_model) > 0:
            self.signalView.selectRow(0)
        else:
            self.signalView.clearSelection()
            # nothing in qt appears to emit selectionChanged when you clear the selection so have to call it ourselves
            self.on_signal_selected()

    def clearSignals(self):
        ''' Deletes all signals '''
        while len(self.__signal_model) > 0:
            self.signalView.selectRow(0)
            self.deleteSignal()

    def importSignal(self):
        '''
        Allows the user to load a signal from a saved file.
        '''

        def parser(file_name):
            with gzip.open(file_name, 'r') as infile:
                return json.loads(infile.read().decode('utf-8'))
        input = self.__load('*.signal', 'Load Signal', parser)
        if input is not None:
            with (wait_cursor()):
                from model.codec import signaldata_from_json
                self.__signal_model.add(signaldata_from_json(input, self.preferences))

    def on_signal_selected(self):
        '''
        Enables the edit & delete button if there are selected rows.
        '''
        selection = self.signalView.selectionModel()
        self.clearSignalsButton.setEnabled(len(self.__signal_model) > 0)
        self.deleteSignalButton.setEnabled(selection.hasSelection())
        if len(selection.selectedRows()) == 1:
            signal_data = self.__get_selected_signal()
            self.__filter_model.filter = signal_data.filter
            with block_signals(self.octaveSmoothing):
                if signal_data.smoothing_type is not None:
                    self.octaveSmoothing.setCurrentText(signal_data.smoothing_description)
                else:
                    self.octaveSmoothing.setCurrentText('None')
            self.__waveform_controller.selected_name = self.__signal_model[selection.selectedRows()[0].row()].name
        else:
            if len(self.__filter_model.filter) > 0:
                self.__default_signal.filter = self.__filter_model.filter
            # we have to set the filter on the default signal and then set that back onto the filter model to ensure
            # the right links are established re listeners and label names
            self.__filter_model.filter = self.__default_signal.filter
            with block_signals(self.octaveSmoothing):
                self.octaveSmoothing.setCurrentText('None')

    def on_filter_change(self, names):
        '''
        Reacts to a change in the filter model by updating the reference, redrawing the chart and other filter related
        things.
        :param names: the signal names.
        '''
        # this can change curve visibility of the signal so need to allow the signalmodel to update visibility
        self.update_reference_series(self.__signal_model.get_visible_curve_names(), self.signalReference, True)
        self.update_reference_series(names, self.filterReference, False)
        self.__magnitude_model.redraw()
        self.__enable_filter_actions()
        self.__check_active_preset(self.__filter_model.filter.preset_idx)
        self.show_y2_tool_buttons(self.showFilters.currentText() != SHOW_NO_FILTERS and len(self.__filter_model) > 0)

    def importFilter(self):
        '''
        Allows the user to replace the current filter with one loaded from a file.
        '''
        from model.filter import load_filter
        filter_json = load_filter(self, self.statusbar)
        if filter_json is not None:
            self.__apply_filter(filter_json)
            self.__magnitude_model.redraw()

    def __apply_filter(self, filter_json):
        from model.codec import filter_from_json
        signal = self.__get_selected_signal()
        filt = filter_from_json(filter_json).resample(signal.fs)
        signal.filter = filt
        self.__filter_model.filter = filt

    def addFilter(self, small=False):
        '''
        Adds a filter via the filter dialog.
        '''
        from model.filter import FilterDialog
        FilterDialog(self.preferences, self.__get_selected_signal(), self.__filter_model,
                     lambda: self.__magnitude_model.redraw(), parent=self, small=small).show()

    def editFilter(self, small=False):
        '''
        Edits the currently selected filter via the filter dialog.
        '''
        selection = self.filterView.selectionModel()
        if selection.hasSelection() and len(selection.selectedRows()) == 1:
            signal = self.__get_selected_signal()
            from model.filter import FilterDialog
            FilterDialog(self.preferences, signal, self.__filter_model,
                         lambda: self.__magnitude_model.redraw(),
                         selected_filter=signal.filter[selection.selectedRows()[0].row()],
                         parent=self, small=small).show()
        else:
            self.addFilter(small=small)

    def deleteFilter(self):
        '''
        Deletes the selected filters.
        '''
        selection = self.filterView.selectionModel()
        if selection.hasSelection():
            self.__filter_model.delete([x.row() for x in selection.selectedRows()])

    def clearFilters(self):
        ''' Deletes all filters  '''
        while len(self.__filter_model) > 0:
            self.filterView.selectRow(0)
            self.deleteFilter()
        self.on_filter_selected()

    def __enable_filter_actions(self):
        '''
        Enables the save filter if we have filters to save.
        '''
        enabled = len(self.__filter_model) > 0
        self.actionSave_Filter.setEnabled(enabled)
        self.actionClear_Filters.setEnabled(enabled)
        self.clearFiltersButton.setEnabled(enabled)

    def on_filter_selected(self):
        '''
        Enables the edit & delete button if there are selected rows.
        '''
        selection = self.filterView.selectionModel()
        self.deleteFilterButton.setEnabled(selection.hasSelection())
        self.editFilterButton.setEnabled(len(selection.selectedRows()) == 1)

    def exportFilter(self):
        '''
        Allows the user to save the current filter to a file.
        '''
        dialog = QFileDialog(parent=self)
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setNameFilter(f"*.filter")
        dialog.setWindowTitle(f"Save Filter")
        dialog.setLabelText(QFileDialog.Accept, 'Save')
        if dialog.exec():
            selected = dialog.selectedFiles()
            if len(selected) > 0:
                if not selected[0].endswith('.filter'):
                    selected[0] += '.filter'
                with open(selected[0], 'w+') as outfile:
                    json.dump(self.__filter_model.filter.to_json(), outfile)
                    self.statusbar.showMessage(f"Saved filter to {outfile.name}")

    def exportChart(self):
        '''
        Saves the currently selected chart to a file.
        '''
        self.__magnitude_model.export_chart(status_bar=self.statusbar)

    def exportReport(self):
        '''
        Saves the currently selected chart to a file.
        '''
        dialog = SaveReportDialog(self, self.preferences, self.__signal_model, self.__filter_model, self.statusbar,
                                  self.__get_selected_signal())
        dialog.exec()

    def exportBiquads(self):
        '''
        Shows the biquads for the current filter set.
        '''
        dialog = ExportBiquadDialog(self.__filter_model.filter, self.preferences)
        dialog.exec()

    def __load(self, filter, title, parser):
        '''
        Presents a file dialog to the user so they can choose something to load.
        :return: the loaded thing, if any.
        '''
        input = None
        dialog = QFileDialog(parent=self)
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter(filter)
        dialog.setWindowTitle(title)
        if dialog.exec():
            selected = dialog.selectedFiles()
            if len(selected) > 0:
                input = parser(selected[0])
                if input is not None:
                    self.statusbar.showMessage(f"Loaded {selected[0]}")
        return input

    def ensurePathContainsExternalTools(self):
        '''
        Ensures that all external tool paths are on the path.
        '''
        path = os.environ.get('PATH', [])
        paths = path.split(os.pathsep)
        locs = self.preferences.get_all(BINARIES_GROUP)
        if len(locs) > 0:
            logging.info(f"Adding {locs} to PATH")
            os.environ['PATH'] = os.pathsep.join([l for l in locs if l not in paths]) + os.pathsep + path
        else:
            logger.warning(f"No {BINARIES_GROUP} paths set")
            # TODO attempt to call each binary with a test command to test if they are really on the path

    def setupUi(self, main_window):
        super().setupUi(self)
        geometry = self.preferences.get(SCREEN_GEOMETRY)
        if geometry is not None:
            self.restoreGeometry(geometry)
        else:
            screen_geometry = self.app.desktop().availableGeometry()
            if screen_geometry.height() < 800:
                self.showMaximized()
        window_state = self.preferences.get(SCREEN_WINDOW_STATE)
        if window_state is not None:
            self.restoreState(window_state)

    def closeEvent(self, *args, **kwargs):
        '''
        Saves the window state on close.
        :param args:
        :param kwargs:
        '''
        self.preferences.set(SCREEN_GEOMETRY, self.saveGeometry())
        self.preferences.set(SCREEN_WINDOW_STATE, self.saveState())
        super().closeEvent(*args, **kwargs)
        self.app.closeAllWindows()

    def showPreferences(self):
        '''
        Shows the preferences dialog.
        '''
        PreferencesDialog(self.preferences, self.__style_path_root, self.__magnitude_model.limits, parent=self).exec()

    def update_reference_series(self, names, combo, primary=True):
        '''
        Updates the reference series dropdown with the current curve names.
        '''
        current_reference = combo.currentText()
        try:
            combo.blockSignals(True)
            combo.clear()
            combo.addItem('None')
            for name in names:
                combo.addItem(name)
            idx = combo.findText(current_reference)
            if idx != -1:
                combo.setCurrentIndex(idx)
            else:
                self.__magnitude_model.normalise(primary=primary)
        finally:
            combo.blockSignals(False)

    def showAbout(self):
        msg_box = QMessageBox()
        msg_box.setText(
            f"<a href='https://github.com/3ll3d00d/beqdesigner'>BEQ Designer</a> v{self.__version} by 3ll3d00d")
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle('About')
        msg_box.exec()

    def showExtractAudioDialog(self):
        '''
        Show the extract audio dialog.
        '''
        from model.extract import ExtractAudioDialog
        ExtractAudioDialog(self, self.preferences, self.__signal_model).show()

    def showRemuxAudioDialog(self):
        '''
        Show the remux audio dialog.
        '''
        from model.extract import ExtractAudioDialog
        ExtractAudioDialog(self, self.preferences, self.__signal_model,
                           default_signal=self.__default_signal, is_remux=True).show()

    def showBatchExtractDialog(self):
        '''
        Show the batch extract dialog.
        '''
        from model.batch import BatchExtractDialog
        BatchExtractDialog(self, self.preferences).show()

    def showAnalyseAudioDialog(self):
        '''
        Show the analyse audio dialog.
        '''
        from model.analysis import AnalyseSignalDialog
        AnalyseSignalDialog(self.preferences, self.__signal_model).exec()

    def showExportFRDDialog(self):
        '''
        Shows the export frd dialog.
        '''
        from model.export import ExportSignalDialog
        ExportSignalDialog(self.preferences, self.__signal_model, self, self.statusbar).exec()

    def showExportSignalDialog(self):
        '''
        Shows the export signal dialog.
        '''
        from model.export import ExportSignalDialog, Mode
        ExportSignalDialog(self.preferences, self.__signal_model, self, self.statusbar, mode=Mode.SIGNAL).exec()

    def exportProject(self):
        '''
        Exports the project to a file.
        '''
        file_name = QFileDialog(self).getSaveFileName(self, 'Export Project', f"project.beq", "BEQ Project (*.beq)")
        file_name = str(file_name[0]).strip()
        if len(file_name) > 0:
            output = self.__signal_model.to_json()
            if not file_name.endswith('.beq'):
                file_name += '.beq'
            with gzip.open(file_name, 'wb+') as outfile:
                outfile.write(json.dumps(output).encode('utf-8'))
            self.statusbar.showMessage(f"Saved project to {file_name}")

    def importProject(self):
        '''
        Allows the user to load a fresh project.
        '''

        def parser(file_name):
            with gzip.open(file_name, 'r') as infile:
                return json.loads(infile.read().decode('utf-8'))
        input = self.__load('*.beq', 'Load Project', parser)
        if input is not None:
            with (wait_cursor()):
                from model.codec import signalmodel_from_json
                self.__signal_model.replace(signalmodel_from_json(input, self.preferences))
                self.__magnitude_model.redraw()

    def normaliseSignalMagnitude(self):
        '''
        Handles reference series change.
        '''
        if self.signalReference.currentText() == 'None':
            self.__magnitude_model.normalise(primary=True)
        else:
            self.__magnitude_model.normalise(primary=True, curve=self.signalReference.currentText())

    def normaliseFilterMagnitude(self):
        '''
        Handles reference series change.
        '''
        if self.filterReference.currentText() == 'None':
            self.__magnitude_model.normalise(primary=False)
        else:
            self.__magnitude_model.normalise(primary=False, curve=self.filterReference.currentText())

    def showLimits(self):
        '''
        Shows the limits dialog for the main chart.
        '''
        self.__magnitude_model.show_limits()

    def showValues(self):
        '''
        Shows the values dialog for the main chart.
        '''
        self.__magnitude_model.show_values()

    def changeFilterVisibility(self, selected_filters):
        '''
        Changes which filters are visible on screen.
        '''
        self.preferences.set(DISPLAY_SHOW_FILTERS, selected_filters)
        self.__filter_model.post_update()
        self.__magnitude_model.redraw()

    def changeSignalVisibility(self, selected_signals):
        '''
        Changes which signals are visible on screen.
        '''
        self.preferences.set(DISPLAY_SHOW_SIGNALS, selected_signals)
        self.__signal_model.post_update()
        self.__magnitude_model.redraw()

    def changeSignalFilterVisibility(self, selected):
        '''
        Changes which filtered signals are visible on screen.
        '''
        self.preferences.set(DISPLAY_SHOW_FILTERED_SIGNALS, selected)
        self.__signal_model.post_update()
        self.__magnitude_model.redraw()

    def changeLegendVisibility(self):
        '''
        Changes whether the legend is visible.
        '''
        self.preferences.set(DISPLAY_SHOW_LEGEND, self.showLegend.isChecked())
        self.__magnitude_model.redraw()

    def toggleTilt(self):
        ''' applies a 3dB/octave tilt to the signals '''
        self.__signal_model.tilt(self.equalEnergyTilt.isChecked())
        self.__magnitude_model.redraw()

    def applyPreset1(self):
        '''
        Applies the preset to the model.
        '''
        self.__apply_preset(1)

    def applyPreset2(self):
        '''
        Applies the preset to the model.
        '''
        self.__apply_preset(2)

    def applyPreset3(self):
        '''
        Applies the preset to the model.
        '''
        self.__apply_preset(3)

    def __apply_preset(self, idx):
        preset_key = FILTERS_PRESET_x % idx
        preset = self.preferences.get(preset_key)
        if preset is not None:
            self.__apply_filter(preset)
            self.__filter_model.filter.preset_idx = idx
            self.__check_active_preset(idx)
            self.on_filter_selected()

    def __check_active_preset(self, preset_idx):
        pattern = re.compile("^preset[0-9]Button$")
        for attr in [at for at in dir(self) if pattern.match(at)]:
            getattr(self, attr).setIcon(QIcon())
        if preset_idx > 0:
            if hasattr(self, f"preset{preset_idx}Button"):
                getattr(self, f"preset{preset_idx}Button").setIcon(qta.icon('fa5s.check'))
            else:
                logger.warning(f"Ignoring attempt to activate an unknown preset {preset_idx}")

    def enable_preset(self, idx):
        preset_key = FILTERS_PRESET_x % idx
        getattr(self, f"preset{idx}Button").setEnabled(self.preferences.has(preset_key))

    def load_preset(self, idx):
        '''
        Allows the user to load a preset from a saved filter.
        :param idx: the index.
        '''
        from model.filter import load_filter

        def __load_preset():
            preset_key = FILTERS_PRESET_x % idx
            input = load_filter(self, self.statusbar)
            if input is not None:
                logger.info(f"Loaded filter for preset {idx}")
                self.preferences.set(preset_key, input)
            self.enable_preset(idx)

        return __load_preset

    def set_preset(self, idx):
        '''
        Saves the current filter to the numbered preset.
        :param idx: the index.
        '''

        def __set_preset():
            preset_key = FILTERS_PRESET_x % idx
            if len(self.__filter_model) > 0:
                input = self.__filter_model.filter.to_json()
                self.preferences.set(preset_key, input)
                self.enable_preset(idx)

        return __set_preset

    def clear_preset(self, idx):
        '''
        Yields a function which will clears the specified preset.
        :param idx: the preset index.
        '''
        prefs = self.preferences
        button = getattr(self, f"preset{idx}Button")

        def __clear_preset():
            prefs.set(FILTERS_PRESET_x % idx, None)
            button.setEnabled(False)

        return __clear_preset

    def add_beq_filter(self):
        '''
        Presents a file dialog to the user so they can choose a minidsp beq filter to load.
        :return: the loaded filter, if any.
        '''
        from model.minidsp import load_as_filter

        filters, filt_file = load_as_filter(self, self.preferences, self.__get_selected_signal().fs)
        if filters is not None:
            self.__load_filter(os.path.splitext(os.path.split(filt_file)[1])[0], filters)
            self.statusbar.showMessage(f"Loaded {filt_file}", 15000)

    def __load_filter(self, description, filters):
        self.clearFilters()
        self.__filter_model.filter.description = description
        for f in filters:
            self.__filter_model.save(f)

    def show_catalogue(self):
        '''
        Shows the catalogue dialog.
        '''
        from model.catalogue import CatalogueDialog
        dialog = CatalogueDialog(self, self.preferences, self.__load_filter)
        dialog.show()
        dialog.setVisible(True)

    def merge_minidsp_xml(self):
        '''
        Shows the merge minidsp XML dialog.
        '''
        from model.merge import MergeFiltersDialog
        dialog = MergeFiltersDialog(self, self.preferences, self.statusbar)
        dialog.exec()

    def create_avs_post(self):
        '''
        Shows the create post dialog.
        '''
        from model.postbuilder import CreateAVSPostDialog
        dialog = CreateAVSPostDialog(self, self.preferences, self.__filter_model, self.__get_selected_signal())
        dialog.exec()

    def sync_htp1(self):
        '''
        displays the Sync HTP1 dialog
        '''
        from model.sync import SyncHTP1Dialog
        dialog = SyncHTP1Dialog(self, self.preferences, self.__signal_model)
        dialog.exec()

    def __import_jriver_peq(self):
        from model.jriver.ui import JRiverDSPDialog
        JRiverDSPDialog(self, self.preferences).exec()

    def show_y2_tool_buttons(self, show=True):
        self.mainChartRightTools.setVisible(show)

    def y2_max_plus_10(self):
        self.__magnitude_model.limits.shift(y2_max=10)

    def y2_max_plus_5(self):
        self.__magnitude_model.limits.shift(y2_max=5)
    
    def y2_max_minus_5(self):
        self.__magnitude_model.limits.shift(y2_max=-5)

    def y2_max_minus_10(self):
        self.__magnitude_model.limits.shift(y2_max=-10)

    def y2_auto_on(self):
        auto = self.y2AutoOnButton.isChecked()
        self.__magnitude_model.limits.y2_auto = auto
        with block_signals(self.y2AutoOffButton):
            self.y2AutoOffButton.setChecked(not auto)

    def y2_auto_off(self):
        auto = self.y2AutoOffButton.isChecked()
        self.__magnitude_model.limits.y2_auto = not auto
        with block_signals(self.y2AutoOnButton):
            self.y2AutoOnButton.setChecked(not auto)

    def y2_min_plus_10(self):
        self.__magnitude_model.limits.shift(y2_min=10)

    def y2_min_plus_5(self):
        self.__magnitude_model.limits.shift(y2_min=5)

    def y2_min_minus_5(self):
        self.__magnitude_model.limits.shift(y2_min=-5)

    def y2_min_minus_10(self):
        self.__magnitude_model.limits.shift(y2_min=-10)

    def y1_max_plus_10(self):
        self.__magnitude_model.limits.shift(y1_max=10)

    def y1_max_plus_5(self):
        self.__magnitude_model.limits.shift(y1_max=5)

    def y1_max_minus_5(self):
        self.__magnitude_model.limits.shift(y1_max=-5)

    def y1_max_minus_10(self):
        self.__magnitude_model.limits.shift(y1_max=-10)

    def y1_auto_on(self):
        auto = self.y1AutoOnButton.isChecked()
        self.__magnitude_model.limits.y1_auto = auto
        with block_signals(self.y1AutoOffButton):
            self.y1AutoOffButton.setChecked(not auto)

    def y1_auto_off(self):
        auto = self.y1AutoOffButton.isChecked()
        self.__magnitude_model.limits.y1_auto = not auto
        with block_signals(self.y1AutoOnButton):
            self.y1AutoOnButton.setChecked(not auto)

    def y1_min_plus_10(self):
        self.__magnitude_model.limits.shift(y1_min=10)

    def y1_min_plus_5(self):
        self.__magnitude_model.limits.shift(y1_min=5)

    def y1_min_minus_5(self):
        self.__magnitude_model.limits.shift(y1_min=-5)

    def y1_min_minus_10(self):
        self.__magnitude_model.limits.shift(y1_min=-10)

    def export_beq_filter(self):
        file_name = QFileDialog(self).getSaveFileName(self, 'Export BEQ Filter', f"beq.xml", "XML (*.xml)")
        file_name = str(file_name[0]).strip()
        if len(file_name) > 0:
            if getattr(sys, 'frozen', False):
                file_path = os.path.join(sys._MEIPASS, 'flat24hd.xml')
            else:
                file_path = os.path.abspath(os.path.join(os.path.dirname('__file__'), '../xml/flat24hd.xml'))
            from model.minidsp import HDXmlParser
            from model.merge import DspType
            parser = HDXmlParser(DspType.MINIDSP_TWO_BY_FOUR_HD, False)
            output_xml, _ = parser.convert(file_path, self.__filter_model.filter)
            with open(file_name, 'w+') as f:
                f.write(output_xml)

    def __open_merge_signal_dialog(self):
        from model.signal import MergeSignalDialog
        MergeSignalDialog(self.preferences, self.__signal_model, parent=self).exec()


class SaveChartDialog(QDialog, Ui_saveChartDialog):
    '''
    Save Chart dialog
    '''

    def __init__(self, parent, name, figure, processor, statusbar=None):
        super(SaveChartDialog, self).__init__(parent)
        self.setupUi(self)
        self.name = name
        self.figure = figure
        self.processor = processor
        self.__x, self.__y = processor.get_dims(self.figure)
        self.__aspectRatio = self.__x / self.__y
        self.widthPixels.setValue(self.__x)
        self.heightPixels.setValue(self.__y)
        self.statusbar = statusbar
        self.__dialog = QFileDialog(parent=self)

    def accept(self):
        formats = "Portable Network Graphic (*.png)"
        file_name = self.__dialog.getSaveFileName(self, 'Export Chart', f"{self.name}.png", formats)
        if file_name:
            output_file = str(file_name[0]).strip()
            if len(output_file) == 0:
                return
            else:
                self.processor.export(self.figure, self.widthPixels.value(), output_file)
                if self.statusbar is not None:
                    self.statusbar.showMessage(f"Saved {self.name} to {output_file}", 5000)
        QDialog.accept(self)

    def set_height(self, newWidth):
        '''
        Updates the height as the width changes according to the aspect ratio.
        :param newWidth: the new width.
        '''
        self.heightPixels.setValue(int(math.floor(newWidth / self.__aspectRatio)))


class MatplotlibExportProcessor:

    def __init__(self, figure):
        self.__figure = figure
        self.__x, self.__y = figure.get_size_inches() * figure.dpi

    def get_dims(self, plot):
        return self.__x, self.__y

    def export(self, plot, width, output_file):
        scale_factor = width / self.__x
        plot.savefig(output_file, format='png', dpi=plot.dpi * scale_factor)


class PyQtGraphExportProcessor:

    @staticmethod
    def get_dims(plot):
        return plot.size().width(), plot.size().height()

    def export(self, plot, width, output_file):
        from pyqtgraph.exporters import ImageExporter
        exporter = ImageExporter(plot.getPlotItem())
        exporter.parameters()['width'] = width
        self.__force_to_int('height', exporter)
        self.__force_to_int('width', exporter)
        exporter.export(output_file)

    @staticmethod
    def __force_to_int(param_name, exporter):
        h = exporter.params.param(param_name)
        orig_h = int(exporter.parameters()[param_name])
        with block_signals(h):
            h.setValue(orig_h + 0.1)
            h.setValue(orig_h)


class ExportBiquadDialog(QDialog, Ui_exportBiquadDialog):
    '''
    Export Biquads Dialog
    '''

    def __init__(self, filter, prefs):
        super(ExportBiquadDialog, self).__init__()
        self.setupUi(self)
        self.__filter = filter
        self.__prefs = prefs
        self.setDefaults.setIcon(qta.icon('fa5s.save'))
        self.copyToClipboardBtn.setIcon(qta.icon('fa5s.clipboard'))
        self.saveToFile.setIcon(qta.icon('fa5s.file-export'))
        self.maxBiquads.setValue(prefs.get(BIQUAD_EXPORT_MAX))
        self.fs.setCurrentText(prefs.get(BIQUAD_EXPORT_FS))
        self.outputFormat.setCurrentText(prefs.get(BIQUAD_EXPORT_DEVICE))
        self.update_format(self.outputFormat.currentText())
        self.outputFormat.addItem('Minidsp DDRC-24')

    def update_format(self, selected_format):
        if selected_format == 'User Selected':
            self.fs.setVisible(True)
            self.fsLabel.setVisible(True)
            self.fs.setEnabled(True)
            self.maxBiquads.setVisible(True)
            self.maxBiquads.setEnabled(True)
            self.maxBiquadsLabel.setVisible(True)
            self.maxBiquads.setMaximum(1000)
            self.maxBiquads.setMinimum(1)
            self.maxBiquads.setSingleStep(1)
            self.showHex.setVisible(False)
        elif selected_format == 'Equalizer APO':
            self.fs.setVisible(False)
            self.fsLabel.setVisible(False)
            self.maxBiquads.setVisible(False)
            self.maxBiquadsLabel.setVisible(False)
            self.showHex.setVisible(False)
        else:
            if selected_format == 'Minidsp 2x4HD':
                self.fs.setCurrentText('96000')
                self.maxBiquads.setMaximum(10)
                self.maxBiquads.setMinimum(1)
                self.maxBiquads.setValue(10)
                self.maxBiquads.setSingleStep(1)
            else:
                self.fs.setCurrentText('48000')
                value = 10 if selected_format == 'Minidsp DDRC-24' else 6
                self.maxBiquads.setMaximum(value)
                self.maxBiquads.setMinimum(value)
                self.maxBiquads.setValue(value)
                self.maxBiquads.setSingleStep(2)
            self.showHex.setVisible('HD' in selected_format)
            self.fs.setEnabled(False)
            self.fs.setVisible(True)
            self.maxBiquads.setVisible(True)
            self.maxBiquadsLabel.setVisible(True)
            self.fsLabel.setVisible(True)
            self.maxBiquads.setEnabled(True)
        if not self.showHex.isVisible():
            self.showHex.setChecked(False)
        self.updateBiquads()

    def updateBiquads(self):
        has_txt = False
        if self.__filter is not None and len(self.__filter) > 0:
            if 'Equalizer APO' == self.outputFormat.currentText():
                text = "\n".join([f"Filter {idx+1}: {t}" for idx, t in enumerate(list(flatten([as_equalizer_apo(f) for f in self.__filter])))])
                if self.__filter.description != COMBINED:
                    text = f"# {self.__filter.description}\n{text}"
            else:
                self.__filter = self.__filter.resample(int(self.fs.currentText()))
                is_fixed_point = 'Minidsp 10x10HD' == self.outputFormat.currentText() or 'Minidsp 2x4' == self.outputFormat.currentText()
                kwargs = {'to_hex': self.showHex.isChecked(), 'fixed_point': is_fixed_point}
                biquads = list(flatten([self.__filter.format_biquads(self.outputFormat.currentText() != 'User Selected',
                                                                     **kwargs)]))
                if len(biquads) < self.maxBiquads.value():
                    passthrough = [Passthrough()] * (self.maxBiquads.value() - len(biquads))
                    biquads += list(flatten([x.format_biquads(self.outputFormat.currentText() != 'User Selected', **kwargs) for x in passthrough]))
                prefix = 'hex' if self.showHex.isChecked() else 'biquad'
                text = ",\n".join([f"{prefix}{idx+1},\n{bq}" for idx, bq in enumerate(biquads)])
            has_txt = len(text.strip()) > 0
            self.biquads.setPlainText(text)
        if not has_txt:
            self.copyToClipboardBtn.setEnabled(False)
            self.saveToFile.setEnabled(False)

    def save(self):
        ''' saves the current preferences '''
        self.__prefs.set(BIQUAD_EXPORT_FS, self.fs.currentText())
        self.__prefs.set(BIQUAD_EXPORT_MAX, self.maxBiquads.value())
        self.__prefs.set(BIQUAD_EXPORT_DEVICE, self.outputFormat.currentText())

    def copyToClipboard(self):
        ''' copies all the text to the clipboard '''
        self.biquads.selectAll()
        self.biquads.copy()
        cursor = self.biquads.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.biquads.setTextCursor(cursor)

    def export(self):
        txt = str(self.biquads.toPlainText()).strip()
        if len(txt) > 0:
            file_name = QFileDialog(self).getSaveFileName(self, 'Export Biquads', f"biquads.txt", "Txt (*.txt)")
            file_name = str(file_name[0]).strip()
            if len(file_name) > 0:
                with open(file_name, 'w') as f:
                    f.write(txt)


def flatten(l):
    '''
    flatten an irregularly shaped list of lists (of lists of lists...)
    solution from https://stackoverflow.com/questions/2158395/flatten-an-irregular-list-of-lists
    '''
    for el in l:
        if isinstance(el, abc.Iterable) and not isinstance(el, (str, bytes)):
            yield from flatten(el)
        else:
            yield el


def make_app():
    app = QApplication(sys.argv)
    if getattr(sys, 'frozen', False):
        icon_path = os.path.join(sys._MEIPASS, 'Icon.ico')
    else:
        icon_path = os.path.abspath(os.path.join(os.path.dirname('__file__'), '../icons/Icon.ico'))
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    prefs = Preferences(QSettings("3ll3d00d", "beqdesigner"))
    if prefs.get(STYLE_MATPLOTLIB_THEME) == f"{STYLE_MATPLOTLIB_THEME_DEFAULT}_extra":
        import qdarkstyle
        style = qdarkstyle.load_stylesheet_from_environment()
        app.setStyleSheet(style)
    return app, prefs


if __name__ == '__main__':
    app, prefs = make_app()
    form = BeqDesigner(app, prefs)
    # setup the error handler
    e_dialog = QErrorMessage(form)
    e_dialog.setWindowModality(QtCore.Qt.WindowModal)
    font = QFont()
    font.setFamily("Consolas")
    font.setPointSize(8)
    e_dialog.setFont(font)
    # add the exception handler so we can see the errors in a QErrorMessage
    sys._excepthook = sys.excepthook


    def dump_exception_to_log(exctype, value, tb):
        import traceback
        print(exctype, value, tb)
        global e_dialog
        if e_dialog is not None:
            formatted = traceback.format_exception(etype=exctype, value=value, tb=tb)
            e_dialog.setWindowTitle('Unexpected Error')
            url = 'https://github.com/3ll3d00d/beqdesigner/issues/new'
            msg = f"Unexpected Error detected, go to {url} to log the issue<p>{'<br>'.join(formatted)}"
            e_dialog.showMessage(msg)
            e_dialog.resize(1200, 400)


    sys.excepthook = dump_exception_to_log

    # show the form and exec the app
    form.show()
    app.exec_()


class PlotWidgetWithDateAxis(pg.PlotWidget):
    def __init__(self, parent=None, background='default', **kargs):
        super().__init__(parent=parent,
                         background=background,
                         axisItems={'bottom': TimeAxisItem(orientation='bottom')},
                         **kargs)


class TimeAxisItem(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        import datetime
        return [str(datetime.timedelta(seconds=value)).split('.')[0] for value in values]


class NoFillDoubleSpinBox(QtWidgets.QDoubleSpinBox):

    def __init__(self, parent=None):
        super().__init__(parent)

    def textFromValue(self, p_float: float):
        txt = super().textFromValue(p_float).rstrip('0')
        return f"{txt}0" if p_float.is_integer() else txt
