import abc
import datetime
import logging
import math
import re
import time
from collections.abc import Sequence
from pathlib import Path
from typing import List, Optional, Dict, Iterable, Any

import numpy as np
import qtawesome as qta
import resampy
from qtpy import QtCore
from qtpy.QtCore import QAbstractTableModel, QModelIndex, QVariant, Qt, QRunnable, QThreadPool
from qtpy.QtWidgets import QDialog, QFileDialog, QDialogButtonBox, QStatusBar
from scipy import signal
from sortedcontainers import SortedDict

from model.codec import signaldata_to_json, bassmanagedsignaldata_to_json
from model.iir import CompleteFilter, ComplexLowPass, FilterType
from model.magnitude import MagnitudeModel
from model.preferences import get_avg_colour, get_peak_colour, get_median_colour, SHOW_FILTERED_ONLY, \
    DISPLAY_SHOW_SIGNALS, DISPLAY_SHOW_FILTERED_SIGNALS, ANALYSIS_TARGET_FS, BASS_MANAGEMENT_LPF_FS, \
    BASS_MANAGEMENT_LPF_POSITION, BM_LPF_BEFORE, BM_LPF_AFTER, DISPLAY_SMOOTH_PRECALC, X_RESOLUTION, \
    SHOWING_AVERAGE, SHOWING_PEAK, SHOWING_MEDIAN, SHOW_UNFILTERED_ONLY, ANALYSIS_WINDOW_DEFAULT, \
    ANALYSIS_RESOLUTION_DEFAULT
from model.xy import MagnitudeData, interp
from ui.merge_signals import Ui_MergeSignalDialog
from ui.signal import Ui_addSignalDialog

SIGNAL_END = 'end'
SIGNAL_START = 'start'
SIGNAL_CHANNEL = 'channel'
SIGNAL_SOURCE_FILE = 'src'

logger = logging.getLogger('signal')

""" speclab reports a peak of 0dB but, by default, we report a peak of -3dB """
SPECLAB_REFERENCE = 1.0 / (2 ** 0.5)


class SignalData(abc.ABC):

    @abc.abstractmethod
    def register_listener(self, listener):
        pass

    @abc.abstractmethod
    def unregister_listener(self, listener):
        pass

    @property
    @abc.abstractmethod
    def duration_seconds(self):
        pass

    @property
    @abc.abstractmethod
    def start_seconds(self):
        pass

    @property
    @abc.abstractmethod
    def duration_hhmmss(self):
        pass

    @property
    @abc.abstractmethod
    def start_hhmmss(self):
        pass

    @property
    @abc.abstractmethod
    def end_hhmmss(self):
        pass

    @property
    @abc.abstractmethod
    def metadata(self):
        pass

    @property
    @abc.abstractmethod
    def signal(self):
        pass

    @property
    @abc.abstractmethod
    def name(self):
        pass

    @property
    @abc.abstractmethod
    def offset(self):
        pass


class SingleChannelSignalData(SignalData):
    '''
    Provides a mechanism for caching the assorted xy data surrounding a signal.
    '''

    def __init__(self, name=None, fs=None, filter=None, xy_data=None, duration_seconds=None, start_seconds=None,
                 signal=None, offset=0.0):
        super().__init__()
        self.__idx = 0
        self.__offset_db = offset
        self.__on_change_listeners = []
        self.__unfiltered: Dict[Optional[int], List[MagnitudeData]] = {}
        self.__filtered = []
        self.__high_pass = False
        self.__smoothing_type = None
        self.__filter = None
        self.__name = None
        self.__signal = signal
        self.slaves = []
        self.master = None
        self.reference_name = None
        self.reference = []
        self.name = name
        if signal is not None:
            self.fs = signal.fs
            self.__duration_seconds = signal.duration_seconds
            self.__start_seconds = signal.start_seconds
            self.smooth(None)
        else:
            self.fs = fs
            self.__duration_seconds = duration_seconds
            self.__start_seconds = start_seconds
            self.__unfiltered[None] = xy_data
        self.filter = filter
        self.tilt_on = False

    @property
    def high_pass(self):
        return self.__high_pass

    @high_pass.setter
    def high_pass(self, high_pass):
        self.__high_pass = high_pass

    @property
    def current_unfiltered(self) -> List[MagnitudeData]:
        return self.__unfiltered[self.__smoothing_type] if self.__smoothing_type in self.__unfiltered else []

    @property
    def current_filtered(self) -> List[MagnitudeData]:
        return self.filtered if self.filtered is not None else []

    @property
    def filtered(self):
        return self.__filtered

    @filtered.setter
    def filtered(self, filtered):
        self.__filtered = filtered

    def register_listener(self, listener):
        ''' registers a listener to be notified when the filter updates (used by the WaveformController) '''
        self.__on_change_listeners.append(listener)

    def unregister_listener(self, listener):
        ''' unregisters a listener to be notified when the filter updates '''
        self.__on_change_listeners.remove(listener)

    @property
    def offset(self):
        return self.__offset_db

    @property
    def duration_seconds(self):
        return self.__duration_seconds

    @property
    def start_seconds(self):
        return self.__start_seconds

    @property
    def duration_hhmmss(self):
        return str(datetime.timedelta(seconds=self.duration_seconds)) if self.duration_seconds is not None else None

    @property
    def start_hhmmss(self):
        return str(datetime.timedelta(seconds=self.start_seconds)) if self.start_seconds is not None else None

    @property
    def end_hhmmss(self):
        return self.duration_hhmmss

    @property
    def metadata(self):
        ''' :return: the metadata from the underlying signal, if any. '''
        return self.signal.metadata if self.signal is not None else None

    @property
    def smoothing_description(self):
        if self.signal is not None and self.__smoothing_type is not None:
            try:
                return f"1/{int(self.smoothing_type)}"
            except:
                return self.smoothing_type
        return ''

    @property
    def smoothing_type(self):
        return self.__smoothing_type if self.signal is not None else None

    @property
    def signal(self):
        '''
        :return: the underlying sample data (may not exist for signals loaded from txt).
        '''
        return self.__signal

    @signal.setter
    def signal(self, signal):
        self.__signal = signal

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = name
        if self.signal is not None:
            self.signal.name = name
        for v in self.filtered:
            v.internal_name = name
        for k, v in self.__unfiltered.items():
            for v1 in v:
                v1.internal_name = name

    @property
    def filter(self):
        return self.__filter

    @property
    def active_filter(self):
        return self.master.filter if self.master is not None else self.filter

    @filter.setter
    def filter(self, filt):
        self.__filter = filt
        if filt is not None:
            self.__filter.listener = self
        self.on_filter_change(filt)

    def __repr__(self) -> str:
        return f"SignalData {self.name}-{self.fs}"

    def reindex(self, idx):
        self.__idx = idx
        self.current_unfiltered[0].colour = get_avg_colour(idx)
        self.current_unfiltered[1].colour = get_peak_colour(idx)
        if len(self.current_unfiltered) == 3:
            self.current_unfiltered[2].colour = get_median_colour(idx)
        if len(self.current_filtered) >= 2:
            self.current_filtered[0].colour = get_avg_colour(idx)
            self.current_filtered[1].colour = get_peak_colour(idx)
            if len(self.current_filtered) == 3:
                self.current_filtered[2].colour = get_median_colour(idx)

    def enslave(self, signal):
        '''
        Allows a signal to be linked to this one so they share the same filter.
        :param signal the signal.
        '''
        logger.debug(f"Enslaving {signal.name} to {self.name}")
        self.slaves.append(signal)
        signal.master = self
        signal.on_filter_change(self.__filter)

    def free_all(self):
        '''
        Frees all slaves.
        '''
        for s in self.slaves:
            logger.debug(f"Freeing {s} from {self}")
            s.master = None
            s.filter = CompleteFilter(fs=self.fs)
        self.slaves = []

    def free(self):
        '''
        if this is a slave, frees itself from the master.
        '''
        if self.master is not None:
            logger.debug(f"Freeing {self.name} from {self.master.name}")
            self.master.slaves.remove(self)
            self.master = None
            self.filter = CompleteFilter(fs=self.fs)

    def smooth(self, smooth_type, set_active=True):
        '''
        applies the given octave fractional smoothing.
        :param smooth_type: the octave fraction, if 0 then remove the smoothing.
        :param set_active: if true, updates the active signal smoothing.
        '''
        if self.__signal is not None:
            if smooth_type is not None and smooth_type == 0:
                smooth_type = None
            if smooth_type not in self.__unfiltered:
                avg = MagnitudeData(self.name, 'avg', self.__signal.avg[0], self.__signal.avg[1],
                                    smooth_type=smooth_type)
                peak = MagnitudeData(self.name, 'peak', self.__signal.peak[0], self.__signal.peak[1],
                                     smooth_type=smooth_type)
                median = MagnitudeData(self.name, 'median', self.__signal.median[0], self.__signal.median[1],
                                       smooth_type=smooth_type)
                self.__unfiltered[smooth_type] = [avg, peak, median]
            if set_active is True:
                self.__smoothing_type = smooth_type
                self.__refresh_filtered(self.__filter)
                self.reindex(self.__idx)

    def get_all_xy(self):
        '''
        :return all the xy data
        '''
        all = self.current_unfiltered + self.current_filtered
        if self.tilt_on:
            all = [mag.with_equal_energy_adjustment() for mag in all]
        return all

    def on_filter_change(self, filt):
        '''
        Updates the cached filtered response when the filter changes.
        :param filt: the filter.
        '''
        logger.debug(f"Applying filter change to {self.name}")
        if filt is None:
            self.filtered = []
            self.__set_unfiltered_linestyle('-')
        elif isinstance(filt, CompleteFilter):
            # TODO detect if the filter has changed and only recalc if it has
            self.__refresh_filtered(filt)
        else:
            raise ValueError(f"Unsupported filter type {filt}")
        for l in self.__on_change_listeners:
            l()
        for s in self.slaves:
            logger.debug(f"Propagating filter change to {s.name}")
            s.on_filter_change(filt)

    def __set_unfiltered_linestyle(self, style):
        for _, v in self.__unfiltered.items():
            for mag in v:
                mag.linestyle = style

    def __refresh_filtered(self, filt):
        if filt is not None:
            unfiltered_avg = self.__unfiltered[None][0]
            unfiltered_peak = self.__unfiltered[None][1]
            filter_mag = filt.get_transfer_function().get_magnitude()
            filtered = [unfiltered_avg.filter(filter_mag).smooth(self.__smoothing_type),
                        unfiltered_peak.filter(filter_mag).smooth(self.__smoothing_type)]
            if len(self.__unfiltered[None]) == 3:
                unfiltered_median = self.__unfiltered[None][2]
                filtered.append(unfiltered_median.filter(filter_mag).smooth(self.__smoothing_type))
            self.filtered = filtered
            self.__set_unfiltered_linestyle('--')

    def tilt(self, tilt):
        ''' applies or removes the equal energy tilt '''
        self.tilt_on = tilt

    def adjust_gain(self, gain):
        '''
        returns the signal with gain adjusted.
        :param gain: the gain.
        :return: the gain adjusted signal.
        '''
        if self.signal is not None:
            return self.signal.adjust_gain(gain)
        return None

    def filter_signal(self, filt=True, clip=False, gain=1.0, pre_filt=None, post_filt=None):
        '''
        returns the filtered signal if we have the raw sample data by transforming the signal via the following steps:
        * adjust_gain
        * pre_filt
        * clip
        * filter
        * post_filt
        * clip
        :param filt: whether to apply the filter.
        :param clip: whether to clip values to a -1.0/1.0 range (both before and after filtering)
        :param gain: the gain.
        :param pre_filt: an additional filter to apply before the active_filter is applied.
        :param post_filt: an additional filter to apply after the active_filter is applied.
        :return: the filtered signal.
        '''
        if self.signal is not None:
            signal = self.signal
            if not math.isclose(gain, 1.0):
                signal = signal.adjust_gain(gain)
            if pre_filt is not None:
                signal = signal.sosfilter(pre_filt.resample(self.fs).get_sos())
            if clip is True:
                signal = signal.clip()
            if filt is True:
                sos = self.active_filter.resample(self.fs, copy_listener=False).get_sos()
                if len(sos) > 0:
                    signal = signal.sosfilter(sos)
            if post_filt is not None:
                signal = signal.sosfilter(post_filt.resample(self.fs).get_sos())
            if clip is True:
                signal = signal.clip()
            return signal
        else:
            return None


class BassManagedSignalData(SignalData):
    ''' A composite signal that will be bass managed. '''

    def __init__(self, signals, lpf_fs, lpf_position, preferences, offset=0.0):
        super().__init__()
        self.__channels = []
        self.__preferences = preferences
        self.__lfe_channel_idx = None
        self.__clip_before = False
        self.__clip_after = False
        self.__offset_db = offset
        for s in signals:
            self.__add(s)
        self.__headroom_type = 'WCS'
        self.__headroom = self.__calc_wcs_headroom()
        self.__lpf_fs = lpf_fs
        self.__lpf_position = lpf_position
        self.__name = signals[0].name[:signals[0].name.rfind('_')]
        self.__fs = signals[0].fs
        self.__duration_seconds = signals[0].duration_seconds
        self.__start_seconds = signals[0].start_seconds
        self.__metadata = {**signals[0].metadata}
        if SIGNAL_CHANNEL in self.__metadata:
            del self.__metadata[SIGNAL_CHANNEL]

    @property
    def offset(self):
        return self.__offset_db

    @property
    def clip_before(self):
        return self.__clip_before

    @clip_before.setter
    def clip_before(self, clip_before):
        self.__clip_before = clip_before

    @property
    def clip_after(self):
        return self.__clip_after

    @clip_after.setter
    def clip_after(self, clip_after):
        self.__clip_after = clip_after

    @property
    def channels(self):
        return self.__channels

    @property
    def bm_headroom_type(self):
        return self.__headroom_type

    @bm_headroom_type.setter
    def bm_headroom_type(self, bm_headroom_type):
        self.__headroom_type = bm_headroom_type
        if self.bm_headroom_type == 'WCS':
            self.__headroom = self.__calc_wcs_headroom()
        else:
            try:
                self.__headroom = abs(float(self.bm_headroom_type)) + 10.0
            except:
                logger.exception(f"Bad bm_headroom {self.bm_headroom_type}")

    @property
    def bm_lpf_position(self):
        return self.__lpf_position

    @bm_lpf_position.setter
    def bm_lpf_position(self, bm_lpf_position):
        self.__lpf_position = bm_lpf_position

    @property
    def bm_lpf_fs(self):
        return self.__lpf_fs

    @property
    def bm_headroom(self):
        return self.__headroom

    def __add(self, signal):
        ''' Adds a new input channel to the signal '''
        if signal.name.endswith('_LFE'):
            self.__lfe_channel_idx = len(self.__channels)
        self.__channels.append(signal)

    def __calc_wcs_headroom(self):
        # calculate the total in dB of coherent summation of the main channels
        main_sum = 20.0 * math.log10(len(self.__channels) - 1)
        # calculate the total of the coherently summed main channels + the LFE channel (as 10dB)
        return 20.0 * math.log10((10.0 ** (main_sum / 20.0)) + (10.0 ** (10.0 / 20.0)))

    def sum(self, apply_filter=True):
        ''' Sums the signals to create a bass managed output '''
        if len(self.__channels) > 1:
            # reduce the main channels by the total amount of headroom
            main_attenuate = 10 ** (-self.bm_headroom / 20.0)
            # and reduce LFE by 10dB less
            lfe_attenuate = 10 ** ((-self.bm_headroom + 10.0) / 20.0)
            logger.debug(
                f"Attenuating {len(self.__channels) - 1} mains by {round(self.bm_headroom, 2)} dB (x{main_attenuate:.4})")
            logger.debug(f"Attenuating LFE by {round(self.bm_headroom - 10, 2)}dB (x{lfe_attenuate:.4})")
            bm_filt = ComplexLowPass(FilterType.LINKWITZ_RILEY, 4, 1000, self.__lpf_fs)
            samples = [x.filter_signal(filt=apply_filter,
                                       pre_filt=bm_filt if self.__lpf_position == BM_LPF_BEFORE else None,
                                       clip=self.__clip_before,
                                       gain=lfe_attenuate if idx == self.__lfe_channel_idx else main_attenuate).samples
                       for idx, x in enumerate(self.__channels)]
            samples = np.sum(np.array(samples), axis=0)
            if self.__lpf_position == BM_LPF_AFTER:
                logger.debug(f"Applying POST BM LPF {bm_filt}")
                samples = signal.sosfilt(bm_filt.get_sos(), samples)
            if self.__clip_after:
                samples = np.clip(samples, -1.0, 1.0)
            return Signal(self.__name, samples, self.__preferences, fs=self.__fs)
        else:
            return self.__channels[0]

    def register_listener(self, listener):
        ''' registers a listener to be notified when the filter updates on each underlying signal '''
        for s in self.__channels:
            s.register_listener(listener)

    def unregister_listener(self, listener):
        ''' unregisters a listener to be notified when the filter updates from each underlying signal '''
        for s in self.__channels:
            s.unregister_listener(listener)

    @property
    def signal(self):
        return self.filter_signal(filt=False)

    def filter_signal(self, filt=True, **kwargs):
        '''
        A filtered and/or clipped signal.
        :param filt: whether to apply the filter.
        :return: the samples.
        '''
        return self.sum(apply_filter=filt)

    @property
    def duration_seconds(self):
        return self.__duration_seconds

    @property
    def start_seconds(self):
        return self.__start_seconds

    @property
    def duration_hhmmss(self):
        return str(datetime.timedelta(seconds=self.__duration_seconds))

    @property
    def start_hhmmss(self):
        return str(datetime.timedelta(seconds=self.__start_seconds))

    @property
    def end_hhmmss(self):
        return self.duration_hhmmss

    @property
    def metadata(self):
        return self.__metadata

    @property
    def name(self):
        return self.__name


class SignalModel(Sequence):
    '''
    A model to hold onto the signals.
    '''

    def __init__(self, view, default_signal, preferences, on_update=lambda _: True):
        self.__signals = []
        self.__bass_managed_signals = []
        self.default_signal = default_signal
        self.__view = view
        self.__on_update = on_update
        self.__preferences = preferences
        self.__table = None

    @property
    def table(self):
        return self.__table

    @property
    def bass_managed_signals(self) -> Iterable[BassManagedSignalData]:
        return self.__bass_managed_signals

    @property
    def non_bm_signals(self):
        return [s for s in self.__signals if not self.__is_bass_managed(s)]

    @table.setter
    def table(self, table):
        self.__table = table

    def __getitem__(self, i):
        return self.__signals[i]

    def __len__(self):
        return len(self.__signals)

    def to_json(self):
        '''
        :return: a json compatible format of the data in the model.
        '''
        json = [bassmanagedsignaldata_to_json(x) for x in self.__bass_managed_signals]
        json += [signaldata_to_json(x) for x in self.__signals if not self.__is_bass_managed(x)]
        return json

    def __is_bass_managed(self, signal):
        '''
        :param signal: the signal.
        :return: true if this signal is found in a bass managed signal.
        '''
        is_bm = False
        for bm in self.__bass_managed_signals:
            for c in bm.channels:
                if c is signal:
                    is_bm = True
                    break
        return is_bm

    def free_all(self):
        '''
        Frees all signals from their masters.
        '''
        if self.__table is not None:
            self.__table.beginResetModel()
        for signal in self:
            signal.free_all()
        if self.__table is not None:
            self.__table.endResetModel()

    def enslave(self, master_name, slave_names):
        '''
        Enslaves the named slaves to the named master.
        :param master_name: the master.
        :param slave_names: the slaves.
        '''
        logger.info(f"Enslaving {slave_names} to {master_name}")
        if self.__table is not None:
            self.__table.beginResetModel()
        master = self.find_by_name(master_name)
        if master is not None:
            for slave_name in slave_names:
                slave = self.find_by_name(slave_name)
                if slave is not None:
                    master.enslave(slave)
        if self.__table is not None:
            self.__table.endResetModel()

    def add(self, signal):
        '''
        Add the supplied signals ot the model.
        :param signals: the signal.
        '''
        if isinstance(signal, BassManagedSignalData):
            # add the bass managed signal first because the selector refresh is driven by the signal model change
            self.__bass_managed_signals.append(signal)
            self.add_all(signal.channels)
        else:
            before_size = len(self.__signals)
            if self.__table is not None:
                self.__table.beginInsertRows(QModelIndex(), before_size, before_size)
            signal.reindex(before_size)
            self.__signals.append(signal)
            self.post_update()
            if self.__table is not None:
                self.__table.endInsertRows()

    def add_all(self, signals):
        '''
        Add the supplied signals ot the model.
        :param signals: the signal.
        '''
        before_size = len(self.__signals)
        if self.__table is not None:
            self.__table.beginInsertRows(QModelIndex(), before_size, before_size + (len(signals) - 1))
        for s in signals:
            s.reindex(len(self.__signals))
            self.__signals.append(s)
        self.post_update()
        if self.__table is not None:
            self.__table.endInsertRows()

    def post_update(self):
        self.__on_update(self.get_visible_curve_names())

    def get_visible_curve_names(self) -> List[str]:
        from app import flatten
        show_signals = self.__preferences.get(DISPLAY_SHOW_SIGNALS)
        show_filtered_signals = self.__preferences.get(DISPLAY_SHOW_FILTERED_SIGNALS)
        pattern = get_visible_signal_name_filter(show_filtered_signals, show_signals)
        visible_signal_names = [x.name for x in flatten([y for x in self.__signals for y in x.get_all_xy()])]
        if pattern is not None:
            visible_signal_names = [x for x in visible_signal_names if pattern.match(x) is not None]
        return visible_signal_names

    def remove(self, signal):
        '''
        Remove the specified signal from the model.
        :param signal: the signal to remove.
        '''
        idx = self.__signals.index(signal)
        if self.__table is not None:
            self.__table.beginRemoveRows(QModelIndex(), idx, idx)
        del self.__signals[idx]
        for idx, s in enumerate(self.__signals):
            s.reindex(idx)
        self.__ensure_master_slave_integrity()
        self.post_update()
        if self.__table is not None:
            self.__table.endRemoveRows()

    def delete(self, indices):
        '''
        Delete the signals at the given indices.
        :param indices: the indices to remove.
        '''
        self.replace([s for idx, s in enumerate(self.__signals) if idx not in indices])

    def get_all_magnitude_data(self):
        '''
        :return: the raw xy data.
        '''
        from app import flatten
        results = list(flatten([s.get_all_xy() for s in self.__signals]))
        return results

    def get_curve_data(self, reference=None):
        '''
        :param reference: the curve against which to normalise.
        :return: the peak,  avg and median spectrum for the signals (if any) + the filter signals.
        '''
        results = self.get_all_magnitude_data()
        show_signals = self.__preferences.get(DISPLAY_SHOW_SIGNALS)
        show_filtered_signals = self.__preferences.get(DISPLAY_SHOW_FILTERED_SIGNALS)
        pattern = get_visible_signal_name_filter(show_filtered_signals, show_signals)
        if pattern is not None:
            results = [x for x in results if pattern.match(x.name) is not None]
        if reference is not None:
            ref_data = next((x for x in results if x.name == reference), None)
            if ref_data:
                results = [x.normalise(ref_data) for x in results]
        return results

    def replace(self, signals):
        '''
        Replaces the contents of the model with the supplied signals
        :param signals: the signals
        '''
        if self.__table is not None:
            self.__table.beginResetModel()
        self.__bass_managed_signals = [s for s in signals if isinstance(s, BassManagedSignalData)]
        sigs = [s for s in signals if isinstance(s, SingleChannelSignalData)]
        for b in self.__bass_managed_signals:
            sigs += b.channels
        self.__signals = sigs
        for idx, s in enumerate(self.__signals):
            if self.__preferences.get(DISPLAY_SMOOTH_PRECALC):
                QThreadPool.globalInstance().start(Smoother(s))
            s.reindex(idx)
        self.__ensure_master_slave_integrity()
        self.__discard_incomplete_bass_managed_signals()
        self.post_update()
        if self.__table is not None:
            self.__table.endResetModel()

    def __discard_incomplete_bass_managed_signals(self):
        ''' discards any bass managed signals that are missing child signals '''
        still_here = []
        for bm in self.__bass_managed_signals:
            if all(c in self.__signals for c in bm.channels):
                still_here.append(bm)
        self.__bass_managed_signals = still_here

    def __ensure_master_slave_integrity(self):
        '''
        Verifies that all master/slaves mentioned by signals actually exist in the model. Used when signals are deleted.
        '''
        for s in self.__signals:
            slave_count_before = len(s.slaves)
            if slave_count_before > 0:
                s.slaves = [slave for slave in s.slaves if slave in self.__signals]
                delta = slave_count_before - len(s.slaves)
                if delta > 0:
                    logger.info(f"Removed {delta} missing slaves from {s.name}")
            if s.master is not None:
                master = next((m for m in self.__signals if m.name == s.master.name), None)
                if master is None:
                    logger.info(f"Removing missing master {s.master.name} from {s.name}")
                    s.free()

    def find_by_name(self, name):
        '''
        :param name: the signal name.
        :return: the signal with that name (or None).
        '''
        return next((s for s in self if s.name == name), None)

    def tilt(self, tilt):
        '''
        Applies or removes the 3dB equal energy tilt.
        :param tilt: true or false.
        '''
        for s in self.__signals:
            s.tilt(tilt)


class Signal:
    """ a source models some input to the analysis system, it provides the following attributes:
        :var samples: an ndarray that represents the signal itself
        :var fs: the sample rate
    """

    def __init__(self, name, samples, preferences=None,
                 analysis_resolution=ANALYSIS_RESOLUTION_DEFAULT, avg_window=ANALYSIS_WINDOW_DEFAULT,
                 peak_window=ANALYSIS_WINDOW_DEFAULT, fs=48000, metadata=None, rescale_x=True):
        if preferences is not None:
            from model.preferences import ANALYSIS_RESOLUTION, ANALYSIS_PEAK_WINDOW, ANALYSIS_AVG_WINDOW
            self.__analysis_resolution = preferences.get(ANALYSIS_RESOLUTION)
            self.__avg_window = preferences.get(ANALYSIS_AVG_WINDOW)
            self.__peak_window = preferences.get(ANALYSIS_PEAK_WINDOW)
        else:
            self.__peak_window = peak_window
            self.__avg_window = avg_window
            self.__analysis_resolution = analysis_resolution
        self.__rescale_x_resolution = rescale_x
        self.__name = name
        self.__x = None
        self.__h = None
        self.samples = samples
        self.fs = fs
        self.duration_seconds = self.samples.size / self.fs
        self.start_seconds = 0
        self.end = self.duration_seconds
        self.__metadata = metadata
        self.__segments = self.__slice_into_large_signal_segments()
        self.__segment_len = self.__segments[0].shape[-1]
        if len(self.__segments) > 1:
            logger.info(f"Split {self.name} into {len(self.__segments)} segments of length {self.__segment_len}")
        self.__avg = None
        self.__peak = None
        self.__median = None

    @property
    def avg(self):
        self.calculate_average()
        return self.__avg

    @property
    def peak(self):
        self.calculate_peak()
        return self.__peak

    @property
    def median(self):
        self.calculate_median()
        return self.__median

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = name

    @property
    def duration_hhmmss(self):
        return str(datetime.timedelta(seconds=self.duration_seconds))

    @property
    def start_hhmmss(self):
        return str(datetime.timedelta(seconds=self.start_seconds))

    @property
    def end_hhmmss(self):
        return self.duration_hhmmss

    @property
    def metadata(self):
        return self.__metadata

    def cut(self, start, end):
        ''' slices a section out of the signal '''
        if start < self.duration_seconds and end <= self.duration_seconds:
            metadata = None
            if self.metadata is not None:
                metadata = {**self.metadata, 'start': start, 'end': end}
            return Signal(self.name,
                          self.samples[int(start * self.fs): int(end * self.fs) + 1],
                          analysis_resolution=self.__analysis_resolution,
                          avg_window=self.__avg_window,
                          peak_window=self.__peak_window,
                          fs=self.fs,
                          metadata=metadata,
                          rescale_x=self.__rescale_x_resolution)
        else:
            return self

    def get_segment_length(self, use_segment=False, resolution_shift=0):
        """
        Calculates a segment length such that the frequency resolution of the resulting analysis is in the region of 
        ~1Hz subject to a lower limit of the number of samples in the signal.
        For example, if we have a 10s signal with an fs is 500 then we convert fs-1 to the number of bits required to 
        hold this number in binary (i.e. 111110011 so 9 bits) and then do 1 << 9 which gives us 100000000 aka 512. Thus
        we have ~1Hz resolution.
        :param resolution_shift: shifts the resolution up or down by the specified number of bits.
        :return: the segment length.
        """
        return min(1 << ((self.fs - 1).bit_length() - int(resolution_shift)),
                   self.__segment_len if use_segment else self.samples.shape[-1])

    def raw(self):
        """
        :return: the raw sample data
        """
        return self.samples

    def avg_spectrum(self, ref=SPECLAB_REFERENCE, resolution_shift=0, window=None, **kwargs):
        """
        analyses the source to generate the linear spectrum.
        :param ref: the reference value for dB purposes.
        :param resolution_shift: allows resolution to go down (if positive) or up (if negative).
        :param mode: cq or none.
        :return:
            f : ndarray
            Array of sample frequencies.
            Pxx : ndarray
            linear spectrum.
        """
        all_kwargs = {'resolution_shift': resolution_shift, 'window': window, **kwargs}
        results = [self.__segment_spectrum(seg, **all_kwargs) for seg in self.__segments]
        if len(results) > 1:
            Pxx_spec = np.mean([r[1] for r in results], axis=0)
        else:
            Pxx_spec = results[0][1]
        f = results[0][0]
        # a 3dB adjustment is required to account for the change in nperseg
        Pxx_spec = amplitude_to_db(np.nan_to_num(np.sqrt(Pxx_spec)), ref * SPECLAB_REFERENCE)
        if self.__rescale_x_resolution is True:
            return self.__rescale_x(f, Pxx_spec)
        else:
            return f, Pxx_spec

    @staticmethod
    def __rescale_x(x, y):
        step = (x[-1] - x[0]) / X_RESOLUTION
        steps = np.arange(x[0], x[-1], step)
        if len(steps) == len(x):
            return x, y
        else:
            import time
            start = time.time()
            x2, y2 = interp(x, y, steps)
            end = time.time()
            logger.debug(f"Interpolation from {len(x)} to {len(x2)} in {round((end - start) * 1000, 3)}ms")
            return x2, y2

    def __segment_spectrum(self, segment, resolution_shift=0, window=None, **kwargs):
        nperseg = self.get_segment_length(use_segment=True, resolution_shift=resolution_shift)
        f, Pxx_spec = signal.welch(segment, self.fs, nperseg=nperseg, scaling='spectrum', detrend=False,
                                   window=window if window else 'hann', **kwargs)
        return f, Pxx_spec

    def peak_spectrum(self, ref=SPECLAB_REFERENCE, resolution_shift=0, window=None):
        """
        analyses the source to generate the max values per bin per segment
        :param resolution_shift: allows resolution to go down (if positive) or up (if negative).
        :param mode: cq or none.
        :param window: window type.
        :return:
            f : ndarray
            Array of sample frequencies.
            Pxx : ndarray
            linear spectrum max values.
        """
        kwargs = {'resolution_shift': resolution_shift, 'window': window}
        results = [self.__segment_peak(seg, **kwargs) for seg in self.__segments]
        if len(results) > 1:
            Pxy_max = np.vstack([r[1] for r in results]).max(axis=0)
        else:
            Pxy_max = results[0][1]
        f = results[0][0]
        # a 3dB adjustment is required to account for the change in nperseg
        Pxy_max = amplitude_to_db(Pxy_max, ref=ref * SPECLAB_REFERENCE)
        return self.__rescale_x(f, Pxy_max)

    def __segment_peak(self, segment, resolution_shift=0, window=None):
        nperseg = self.get_segment_length(use_segment=True, resolution_shift=resolution_shift)
        freqs, _, Pxy = signal.spectrogram(segment,
                                           self.fs,
                                           window=window if window else ('tukey', 0.25),
                                           nperseg=int(nperseg),
                                           noverlap=int(nperseg // 2),
                                           detrend=False,
                                           scaling='spectrum')
        Pxy_max = np.sqrt(Pxy.max(axis=-1).real)
        return freqs, Pxy_max

    def spectrogram(self, ref=SPECLAB_REFERENCE, resolution_shift=0, window=None):
        """
        analyses the source to generate a spectrogram
        :param resolution_shift: allows resolution to go down (if positive) or up (if negative).
        :return:
            f : ndarray
            Array of time slices.
            t : ndarray
            Array of sample frequencies.
            Pxx : ndarray
            linear spectrum values.
        """
        nperseg = self.get_segment_length(resolution_shift=resolution_shift)
        f, t, Sxx = signal.spectrogram(self.samples,
                                       self.fs,
                                       window=window if window else ('tukey', 0.25),
                                       nperseg=nperseg,
                                       noverlap=int(nperseg // 2),
                                       detrend=False,
                                       scaling='spectrum')
        Sxx = amplitude_to_db(np.sqrt(Sxx), ref=ref * SPECLAB_REFERENCE)
        return f, t, Sxx

    def filter(self, a, b):
        """
        Applies a digital filter via filtfilt.
        :param a: the a coeffs.
        :param b: the b coeffs.
        :return: the filtered signal.
        """
        return Signal(self.name,
                      signal.filtfilt(b, a, self.samples),
                      analysis_resolution=self.__analysis_resolution,
                      avg_window=self.__avg_window,
                      peak_window=self.__peak_window,
                      fs=self.fs,
                      metadata=self.metadata,
                      rescale_x=self.__rescale_x_resolution)

    def sosfilter(self, sos, filtfilt=False):
        '''
        Applies a cascaded 2nd order series of filters.
        :param filtfilt: use sosfiltfilt if true else sosfilt.
        :param sos: the sections.
        :return: the filtered signal
        '''
        call = signal.sosfiltfilt if filtfilt else signal.sosfilt
        return Signal(self.name,
                      call(sos, self.samples),
                      analysis_resolution=self.__analysis_resolution,
                      avg_window=self.__avg_window,
                      peak_window=self.__peak_window,
                      fs=self.fs,
                      metadata=self.metadata,
                      rescale_x=self.__rescale_x_resolution)

    def invert(self):
        '''
        Inverts the signal
        :return: the inverted signal
        '''
        return Signal(self.name,
                      self.samples * -1,
                      analysis_resolution=self.__analysis_resolution,
                      avg_window=self.__avg_window,
                      peak_window=self.__peak_window,
                      fs=self.fs,
                      metadata=self.metadata,
                      rescale_x=self.__rescale_x_resolution)

    def zero(self):
        '''
        zeroes the signal
        :return: the zeroed signal
        '''
        return Signal(self.name,
                      np.zeros(self.samples.shape),
                      analysis_resolution=self.__analysis_resolution,
                      avg_window=self.__avg_window,
                      peak_window=self.__peak_window,
                      fs=self.fs,
                      metadata=self.metadata,
                      rescale_x=self.__rescale_x_resolution)

    def copy(self, new_name=None):
        '''
        Copies the signal, optionally setting a new name.
        :param new_name: the new name, if any.
        :return: the copied signal.
        '''
        copy = self.shift(0)
        if new_name:
            copy.name = new_name
        return copy

    def shift(self, millis: float, subsample: bool = False):
        '''
        shifts the signal by the specified no of samples while retaining signal length.
        :param millis: amount to shift by, negative means left shift (i.e. play earlier), positive means right
        shift (i.e. play later).
        :param subsample: whether to apply a subsample shift
        :return: the shifted signal.
        '''
        samples_exact = (millis / 1000) * self.fs
        samples = math.floor(samples_exact)
        fraction = samples_exact - samples

        if samples:
            if samples > 0:
                new_samples = np.insert(self.samples, 0, np.zeros(samples))[:-samples]
            else:
                new_samples = np.append(self.samples, np.zeros(-samples))[-samples:]
        else:
            new_samples = np.copy(self.samples)

        if not math.isclose(fraction, 0.0):
            if subsample:
                # TODO 1st order APF does not work as intended, use an FIR filter instead
                frac = 1.0 - fraction
                coeffs = [frac, 1.0, 0.0, 1.0, frac, 0.0]
                new_samples = signal.sosfiltfilt(coeffs, self.samples)
            else:
                # print(f"Ignoring {fraction:.4f} samples")
                pass

        return Signal(self.name,
                      new_samples,
                      analysis_resolution=self.__analysis_resolution,
                      avg_window=self.__avg_window,
                      peak_window=self.__peak_window,
                      fs=self.fs,
                      metadata=self.metadata,
                      rescale_x=self.__rescale_x_resolution)

    def adjust_gain(self, gain):
        '''
        Adjusts the gain via the specified gain factor (ratio)
        :param gain: the gain ratio to apply.
        :return: the adjusted signal.
        '''
        return Signal(self.name,
                      self.samples * gain,
                      analysis_resolution=self.__analysis_resolution,
                      avg_window=self.__avg_window,
                      peak_window=self.__peak_window,
                      fs=self.fs,
                      metadata=self.metadata,
                      rescale_x=self.__rescale_x_resolution)

    def offset(self, offset):
        '''
        Adjusts the gain via the specified offset (in dB).
        :param gain: the offset in dB to apply.
        :return: the adjusted signal.
        '''
        if not math.isclose(offset, 0.0):
            return self.adjust_gain(10 ** (offset / 20.0))
        else:
            return self

    def clip(self, amin=-1.0, amax=1.0):
        '''
        Clamps the samples to the given range.
        :param amin: the min value.
        :param amax: the max value.
        :return: the clipped signal.
        '''
        return Signal(self.name,
                      np.clip(self.samples, amin, amax),
                      analysis_resolution=self.__analysis_resolution,
                      avg_window=self.__avg_window,
                      peak_window=self.__peak_window,
                      fs=self.fs,
                      metadata=self.metadata,
                      rescale_x=self.__rescale_x_resolution)

    def add(self, samples):
        '''
        Adds the provided samples to this signal. Ensures the signals have the same shape is left to the caller.
        :param samples: the samples
        :return: a new signal.
        '''
        return Signal(self.name,
                      self.samples + (samples.samples if isinstance(samples, Signal) else samples),
                      analysis_resolution=self.__analysis_resolution,
                      avg_window=self.__avg_window,
                      peak_window=self.__peak_window,
                      fs=self.fs,
                      metadata=self.metadata,
                      rescale_x=self.__rescale_x_resolution)

    def subtract(self, samples):
        '''
        Subtracts the provided samples from this signal. Ensures the signals have the same shape is left to the caller.
        :param samples: the samples
        :return: a new signal.
        '''
        return Signal(self.name,
                      self.samples - (samples.samples if isinstance(samples, Signal) else samples),
                      analysis_resolution=self.__analysis_resolution,
                      avg_window=self.__avg_window,
                      peak_window=self.__peak_window,
                      fs=self.fs,
                      metadata=self.metadata,
                      rescale_x=self.__rescale_x_resolution)

    def resample(self, new_fs):
        '''
        Resamples to the new fs (if required).
        :param new_fs: the new fs.
        :return: the signal
        '''
        if new_fs != self.fs:
            start = time.time()
            resampled = Signal(self.name,
                               resampy.resample(self.samples, self.fs, new_fs, filter=self.load_resampy_filter()),
                               analysis_resolution=self.__analysis_resolution,
                               avg_window=self.__avg_window,
                               peak_window=self.__peak_window,
                               fs=new_fs,
                               metadata=self.metadata,
                               rescale_x=self.__rescale_x_resolution)
            end = time.time()
            logger.info(f"Resampled {self.name} from {self.fs} to {new_fs} in {round(end - start, 3)}s")
            return resampled
        else:
            return self

    def load_resampy_filter(self):
        '''
        A replacement for resampy.load_filter that is compatible with pyinstaller.
        :return: same values as resampy.load_filter
        '''
        import sys
        if getattr(sys, 'frozen', False):
            def __load_frozen():
                import os
                data = np.load(
                    os.path.join(sys._MEIPASS, '_resampy_filters', os.path.extsep.join(['kaiser_fast', 'npz'])))
                return data['half_window'], data['precision'], data['rolloff']

            return __load_frozen
        else:
            return 'kaiser_fast'

    def calculate_average(self):
        '''
        caches the avg spectrum if we have no data.
        '''
        if self.__avg is None:
            resolution_shift = int(math.log(self.__analysis_resolution, 2))
            avg_wnd = self.__get_window(self.__avg_window)
            logger.debug(
                f"Analysing {self.name} at {self.__analysis_resolution} Hz resolution using {avg_wnd if avg_wnd else 'Default'} avg windows")
            self.__avg = self.avg_spectrum(resolution_shift=resolution_shift, window=avg_wnd, average='mean')

    def calculate_peak(self):
        '''
        caches the peak spectrum if we have no data.
        '''
        if self.__peak is None:
            resolution_shift = int(math.log(self.__analysis_resolution, 2))
            peak_wnd = self.__get_window(self.__peak_window)
            logger.debug(
                f"Analysing {self.name} at {self.__analysis_resolution} Hz resolution using {peak_wnd if peak_wnd else 'Default'} peak windows")
            self.__peak = self.peak_spectrum(resolution_shift=resolution_shift, window=peak_wnd)

    def calculate_median(self):
        '''
        caches the median spectrum if we have no data.
        '''
        if self.__median is None:
            resolution_shift = int(math.log(self.__analysis_resolution, 2))
            avg_wnd = self.__get_window(self.__avg_window)
            self.__median = self.avg_spectrum(resolution_shift=resolution_shift, window=avg_wnd, average='median')

    def calculate_peak_average(self):
        '''
        caches the peak, avg and median spectrum if we have no data.
        '''
        self.calculate_average()
        self.calculate_peak()
        self.calculate_median()

    def __slice_into_large_signal_segments(self):
        '''
        split into equal sized chunks of no greater than 10mins of a 48kHz track size
        '''
        max_segment_length = 10 * 60 * 48000
        segments = math.ceil(self.samples.size / float(max_segment_length))
        if segments > 1:
            target_segment_length = math.ceil(self.samples.size / segments)
            segments = list(range(target_segment_length, self.samples.size, target_segment_length))
            split_samples = np.split(self.samples, segments)
            to_pad = split_samples[0].size - split_samples[-1].size
            if to_pad > 0:
                split_samples[-1] = np.pad(split_samples[-1], (0, to_pad), constant_values=0)
            return split_samples
        else:
            return [self.samples]

    @staticmethod
    def __get_window(window):
        from model.preferences import ANALYSIS_WINDOW_DEFAULT
        if window is None or window == ANALYSIS_WINDOW_DEFAULT:
            window = None
        else:
            if window == 'tukey':
                window = (window, 0.25)
        return window

    @property
    def step_response(self):
        t = self.__time_series()
        from scipy import integrate
        sr = integrate.cumulative_trapezoid(self.samples, t, initial=0)
        return t, sr

    @property
    def waveform(self):
        return self.__time_series(), self.copy().samples

    @property
    def phase_response(self):
        x, h = self.__freqz()
        return x, np.angle(h, deg=True)

    @property
    def mag_response(self):
        x, h = self.__freqz()
        h[h == 0] = 0.000000001
        return x, 20 * np.log10(abs(h))

    def __freqz(self):
        if self.__x is None:
            w, self.__h = signal.freqz(self.samples, worN=1 << (int(self.fs / 2) - 1).bit_length())
            self.__x = w * self.fs * 1.0 / (2 * np.pi)
        return self.__x, self.__h

    def __time_series(self):
        return np.arange(start=0.0, stop=self.samples.size / self.fs, step=1 / self.fs)

    @property
    def peak_pos(self) -> float:
        return self.__time_series()[np.argmax(self.samples)]

    def __repr__(self):
        return f"Signal {self.name} {{fs: {self.fs}, len: {len(self.samples)}}}"


def amplitude_to_db(s, ref=1.0):
    '''
    Convert an amplitude spectrogram to dB-scaled spectrogram. Implementation taken from librosa to avoid adding a
    dependency on librosa for a few util functions.
    :param s: the amplitude spectrogram.
    :return: s_db : np.ndarray ``s`` measured in dB
    '''
    magnitude = np.abs(np.asarray(s))
    power = np.square(magnitude, out=magnitude)
    ref_power = np.abs(ref ** 2)
    amin = 1e-20
    top_db = 80.0
    log_spec = 10.0 * np.log10(np.maximum(amin, power))
    log_spec -= 10.0 * np.log10(np.maximum(amin, ref_power))
    log_spec = np.maximum(log_spec, log_spec.max() - top_db)
    return log_spec


def db_to_amplitude(s, ref=1.0):
    '''
    Convert a dB-scaled spectrogram to an amplitude spectrogram. Implementation taken from librosa to avoid adding a
    dependency on librosa for a few util functions.

    This effectively inverts `amplitude_to_db`:

        `db_to_amplitude(S_db) ~= 10.0**(0.5 * (S_db + log10(ref)/10))`

    :param s: the dB scaled spectrogram.
    :param ref: reference power.
    :return: s_lin : Linear magnitude spectrogram
    '''
    return db_to_power(s, ref=ref ** 2) ** 0.5


def db_to_power(s, ref=1.0):
    '''
    Convert a dB-scale spectrogram to a power spectrogram. Implementation taken from librosa to avoid adding a
    dependency on librosa for a few util functions.

    This effectively inverts `power_to_db`:

        `db_to_power(S_db) ~= ref * 10.0**(S_db / 10)`

    :param s: the dB scaled spectrogram.
    :param ref: reference power.
    :return: s_lin : Linear magnitude spectrogram
    '''
    return ref * np.power(10.0, 0.1 * s)


class SignalTableModel(QAbstractTableModel):
    '''
    A Qt table model to feed the signal view.
    '''

    def __init__(self, model, parent=None):
        super().__init__(parent=parent)
        self.__headers = ['Name', 'Linked', 'Fs', 'Duration', 'Offset']
        self.__signal_model = model
        self.__signal_model.table = self

    def rowCount(self, parent: QModelIndex = ...):
        return len(self.__signal_model)

    def columnCount(self, parent: QModelIndex = ...):
        return len(self.__headers)

    def flags(self, idx):
        flags = super().flags(idx)
        if idx.column() == 0:
            flags |= Qt.ItemIsEditable
        return flags

    def setData(self, idx, value, role=None):
        if idx.column() == 0:
            self.__signal_model[idx.row()].name = value
            self.dataChanged.emit(idx, idx, [])
            return True
        return super().setData(idx, value, role=role)

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        if not index.isValid():
            return QVariant()
        elif role != Qt.DisplayRole:
            return QVariant()
        else:
            signal_at_row = self.__signal_model[index.row()]
            if index.column() == 0:
                return QVariant(signal_at_row.name)
            if index.column() == 1:
                if signal_at_row.master is not None:
                    return QVariant(f"S - {signal_at_row.master.name}")
                elif len(signal_at_row.slaves) > 0:
                    return QVariant(f"M {len(signal_at_row.slaves)}")
                else:
                    return QVariant('')
            elif index.column() == 2:
                return QVariant(signal_at_row.fs)
            elif index.column() == 3:
                return QVariant(signal_at_row.duration_hhmmss)
            elif index.column() == 4:
                return QVariant(signal_at_row.offset)
            else:
                return QVariant()

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> Any:
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.__headers[section])
        return QVariant()


def select_file(owner, file_types):
    '''
    Presents a file picker for selecting a file that contains a signal.
    '''
    dialog = QFileDialog(parent=owner)
    dialog.setFileMode(QFileDialog.ExistingFile)
    filt = ' '.join([f"*.{f}" for f in file_types])
    dialog.setNameFilter(f"Audio ({filt})")
    dialog.setWindowTitle(f"Select Signal File")
    if dialog.exec():
        selected = dialog.selectedFiles()
        if len(selected) > 0:
            return selected[0]
    return None


class AutoWavLoader:
    '''
    Loads signals from wav files without user interaction
    '''

    def __init__(self, preferences):
        self.__cache = SortedDict()
        self.__preferences = preferences
        self.__start = None
        self.__end = None
        self.info = None
        self.__wav_data = None

    def clear_cache(self):
        ''' Empties the internal signal cache. '''
        self.__cache = SortedDict()

    def reset(self):
        '''
        Clears internal state.
        '''
        self.clear_cache()
        self.__wav_data = None
        self.info = None

    def auto_load(self, name_provider, decimate, offset=0.0):
        '''
        Loads the file and automatically creates a signal for each channel found.
        :param name_provider: a callable that yields a signal name for the given channel.
        :param decimate: if true, decimate
        :param offset: the gain offset to apply in dB
        :return: the signals.
        '''
        start = time.time()
        try:
            for x in range(0, self.info.channels):
                self.prepare(channel=x + 1, name=name_provider(x, self.info.channels),
                             channel_count=self.info.channels,
                             decimate=decimate)
            if self.info.channels > 1:
                signals = [self.get_signal(x, name_provider(x - 1, self.info.channels), offset=offset)
                           for x in self.__cache.keys()]
                lpf_fs = self.__preferences.get(BASS_MANAGEMENT_LPF_FS)
                lpf_position = self.__preferences.get(BASS_MANAGEMENT_LPF_POSITION)
                return BassManagedSignalData(signals, lpf_fs, lpf_position, self.__preferences)
            else:
                return self.get_signal(1, name_provider(0, 1), offset=offset)
        finally:
            logger.info(f"Loaded {self.info.channels} from {self.info.name} in {round(time.time() - start, 3)}s")

    def load(self, file):
        '''
        Gets info about the file.
        :param file: the file.
        :return: if auto is True, a signal for each channel.
        '''
        self.reset()
        import soundfile as sf
        before = time.time()
        self.info = sf.info(file)
        self.__wav_data = read_wav_data(file, start=self.__start, end=self.__end)
        after = time.time()
        logger.debug(f"Read {file} in {round(after - before, 3)}s")

    def set_range(self, start=None, end=None):
        '''
        Sets the range to load from the file.
        :param start: the start position, if any.
        :param end: the end position, if any.
        '''
        if self.__start != start or self.__end != end:
            logger.debug("Resetting loader on time range change, new range is {start}-{end}")
            old_info = self.info
            self.reset()
            self.__start = start
            self.__end = end
            if old_info is not None:
                self.load(old_info.name)

    def prepare(self, name=None, channel_count=1, channel=1, decimate=True):
        '''
        analyses a single channel from the wav with the specified parameters, caching the result for future reuse.
        :param name: the signal name, if none use the file name + channel.
        :param channel: the channel
        :param channel_count: the channel count, only used for creating a default name.
        :param decimate: if true, decimate the wav.
        '''
        if name is None or len(name.strip()) == 0:
            name = Path(self.info.name).resolve().stem
            if channel_count > 1:
                name += f"_c{channel}"
        if channel not in self.__cache:
            from model.preferences import ANALYSIS_TARGET_FS
            target_fs = self.__preferences.get(ANALYSIS_TARGET_FS) if decimate is True else self.info.samplerate
            signal = readWav(name, self.__preferences, input_data=self.__wav_data, channel=channel, target_fs=target_fs)
            self.__cache[channel] = SingleChannelSignalData(name=name, signal=signal)
        else:
            if name is not None:
                self.__cache[channel].name = name

    def get_signal(self, channel_idx, name, offset=0.0):
        '''
        Converts the loaded signal into a SignalData.
        :return: the signal data.
        '''
        signal = self.__cache[channel_idx].signal
        if not math.isclose(offset, 0.0):
            signal = signal.offset(offset)
        signal.name = name
        return SingleChannelSignalData(name=name,
                                       filter=CompleteFilter(fs=signal.fs),
                                       signal=signal,
                                       offset=offset)

    def get_magnitude_data(self, channel_idx):
        '''
        :param channel_idx: the channel.
        :return: magnitude data for this signal, if we have one.
        '''
        if channel_idx in self.__cache:
            return self.__cache[channel_idx].current_unfiltered
        else:
            return []

    def has_signal(self):
        '''
        :return: True if we have a signal.
        '''
        return len(self.__cache) > 0

    def toggle_decimate(self):
        pass


class DialogWavLoaderBridge:
    '''
    Loads signals from wav files.
    '''

    def __init__(self, dialog, preferences, allow_multichannel=True):
        self.__preferences = preferences
        self.__dialog = dialog
        self.__auto_loader = AutoWavLoader(preferences)
        self.__duration = 0
        self.__allow_multichannel = allow_multichannel

    def toggle_decimate(self, channel_idx):
        self.__auto_loader.clear_cache()
        self.prepare_signal(channel_idx)

    def select_wav_file(self):
        file = select_file(self.__dialog, ['wav', 'flac'])
        if file is not None:
            self.clear_signal()
            self.__dialog.wavFile.setText(file)
            self.init_time_range()
            self.__auto_loader.load(file)
            self.__load_info()

    def clear_signal(self):
        self.__auto_loader.reset()
        self.__duration = 0
        self.__dialog.wavStartTime.setEnabled(False)
        self.__dialog.wavEndTime.setEnabled(False)
        self.__dialog.gainOffset.setEnabled(False)
        self.__dialog.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

    def __load_info(self):
        '''
        Loads metadata about the signal from the file and propagates it to the form fields.
        '''
        info = self.__auto_loader.info
        self.__dialog.wavFs.setText(f"{info.samplerate} Hz")
        self.__dialog.decimate.setEnabled(info.samplerate != self.__preferences.get(ANALYSIS_TARGET_FS))
        from model.report import block_signals
        with block_signals(self.__dialog.wavChannelSelector):
            self.__dialog.wavChannelSelector.clear()
            for i in range(0, info.channels):
                self.__dialog.wavChannelSelector.addItem(f"{i + 1}")
            self.__dialog.wavChannelSelector.setEnabled(info.channels > 1)
        self.__dialog.loadAllChannels.setEnabled(info.channels > 1 and self.__allow_multichannel)
        with block_signals(self.__dialog.wavStartTime):
            self.__dialog.wavStartTime.setTime(QtCore.QTime(0, 0, 0))
            self.__dialog.wavStartTime.setEnabled(True)
        self.__duration = math.floor(info.duration * 1000)
        with block_signals(self.__dialog.wavEndTime):
            self.__dialog.wavEndTime.setTime(QtCore.QTime(0, 0, 0).addMSecs(self.__duration))
            self.__dialog.wavEndTime.setEnabled(True)
        self.__dialog.wavSignalName.setEnabled(True)
        self.prepare_signal(int(self.__dialog.wavChannelSelector.currentText()))
        self.__dialog.applyTimeRangeButton.setEnabled(False)

    def init_time_range(self):
        ''' Initialises the time range on the auto loader. '''
        start = end = None
        start_millis = self.__dialog.wavStartTime.time().msecsSinceStartOfDay()
        if start_millis > 0:
            start = start_millis
        end_millis = self.__dialog.wavEndTime.time().msecsSinceStartOfDay()
        if end_millis < self.__duration or start is not None:
            end = end_millis
        self.__auto_loader.set_range(start=start, end=end)

    def prepare_signal(self, channel_idx):
        '''
        Reads the actual file and calculates the relevant peak/avg spectrum.
        '''
        self.__auto_loader.prepare(name=self.__dialog.wavSignalName.text(),
                                   channel=channel_idx,
                                   decimate=self.__dialog.decimate.isChecked())
        self.__dialog.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
        self.__dialog.gainOffset.setEnabled(True)

    def __get_window(self, key):
        from model.preferences import ANALYSIS_WINDOW_DEFAULT
        window = self.__preferences.get(key)
        if window is None or window == ANALYSIS_WINDOW_DEFAULT:
            window = None
        else:
            if window == 'tukey':
                window = (window, 0.25)
        return window

    def get_magnitude_data(self):
        if self.__dialog.wavChannelSelector.count() > 0:
            return self.__auto_loader.get_magnitude_data(int(self.__dialog.wavChannelSelector.currentText()))
        else:
            return []

    def can_save(self):
        '''
        :return: true if we can save a new signal.
        '''
        return self.__auto_loader.has_signal()

    def enable_ok(self):
        enabled = len(
            self.__dialog.wavSignalName.text()) > 0 and not self.__dialog.applyTimeRangeButton.isEnabled() and self.can_save()
        self.__dialog.buttonBox.button(QDialogButtonBox.Ok).setEnabled(enabled)
        return enabled

    def get_signal(self, offset=0.0):
        '''
        Converts the loaded signal into a SignalData.
        :return: the signal data.
        '''
        if self.__dialog.loadAllChannels.isChecked() and self.__dialog.loadAllChannels.isEnabled():
            from model.extract import get_channel_name
            name_provider = lambda channel, channel_count: get_channel_name(self.__dialog.wavSignalName.text(), channel,
                                                                            channel_count)
            return self.__auto_loader.auto_load(name_provider,
                                                self.__dialog.decimate.isChecked(),
                                                offset=offset)
        else:
            return self.__auto_loader.get_signal(int(self.__dialog.wavChannelSelector.currentText()),
                                                 self.__dialog.wavSignalName.text(),
                                                 offset=offset)


class FrdLoader:
    '''
    Loads signals from frd files.
    '''

    def __init__(self, dialog):
        self.__dialog = dialog
        self.__peak = None
        self.__avg = None

    def _read_from_file(self):
        file = select_file(self.__dialog, ['frd'])
        if file is not None:
            comment_char = None
            with open(file) as f:
                c = f.read(1)
                if not c.isalnum():
                    comment_char = c
            f, m = np.genfromtxt(file, comments=comment_char, unpack=True)
            return file, f, m
        return None, None, None

    def select_peak_file(self):
        '''
        Asks the user to pick a file containing the peak series magnitude response.
        '''
        name, f, m = self._read_from_file()
        if name is not None:
            signal_name = Path(name).resolve().stem
            if signal_name.endswith('_filter_peak'):
                signal_name = signal_name[:-12]
            elif signal_name.endswith('_peak'):
                signal_name = signal_name[:-5]
            self.__peak = MagnitudeData(signal_name, 'peak', f, m, colour=get_peak_colour(0))
            self.__dialog.frdSignalName.setText(signal_name)
            self.__dialog.frdPeakFile.setText(name)
            self.__enable_fields()

    def select_avg_file(self):
        '''
        Asks the user to pick a file containing the avg series magnitude response.
        '''
        name, f, m = self._read_from_file()
        if name is not None:
            signal_name = Path(name).resolve().stem
            if signal_name.endswith('_filter_avg'):
                signal_name = signal_name[:-11]
            elif signal_name.endswith('_avg'):
                signal_name = signal_name[:-4]
            self.__avg = MagnitudeData(signal_name, 'avg', f, m, colour=get_avg_colour(0))
            self.__dialog.frdSignalName.setText(signal_name)
            self.__dialog.frdAvgFile.setText(name)
            self.__enable_fields()

    def __enable_fields(self):
        '''
        Enables the fs field if we have both measurements.
        '''
        self.__dialog.frdSignalName.setEnabled(self.__peak is not None or self.__avg is not None)
        if self.__peak is not None and self.__avg is not None:
            # TODO read the header?
            self.__dialog.frdFs.setValue(int(np.max(self.__peak.x) * 2))
            self.__dialog.frdFs.setEnabled(True)
        self.enable_ok()

    def enable_ok(self):
        enabled = len(self.__dialog.frdSignalName.text()) > 0 and self.can_save()
        self.__dialog.buttonBox.button(QDialogButtonBox.Ok).setEnabled(enabled)
        return enabled

    def clear_signal(self):
        self.__peak = None
        self.__avg = None
        self.__enable_fields()

    def get_magnitude_data(self):
        data = []
        if self.__avg is not None:
            data.append(self.__avg)
        if self.__peak is not None:
            data.append(self.__peak)
        return data

    def can_save(self):
        return self.__avg is not None and self.__peak is not None

    def get_signal(self, **kwargs):
        frd_name = self.__dialog.frdSignalName.text()
        self.__avg.internal_name = frd_name
        self.__peak.internal_name = frd_name
        return SingleChannelSignalData(name=frd_name,
                                       fs=self.__dialog.frdFs.value(),
                                       filter=CompleteFilter(fs=self.__dialog.frdFs.value()),
                                       xy_data=self.get_magnitude_data())


class PulseLoader:
    '''
    Generates pulse signals.
    '''

    def __init__(self, dialog, prefs):
        self.__dialog = dialog
        self.__prefs = prefs
        from scipy.signal import unit_impulse
        signal = Signal('signal', unit_impulse(4 * 48000, 'mid'), prefs, fs=48000)
        self.__pulse = SingleChannelSignalData(name=f"signal", signal=signal)

    def can_save(self):
        '''
        :return: true if we can save at least one signal.
        '''
        return len(self.__dialog.pulsePrefix.text()) > 0

    def enable_ok(self):
        enabled = self.can_save()
        self.__dialog.buttonBox.button(QDialogButtonBox.Ok).setEnabled(enabled)
        return enabled

    def get_magnitude_data(self):
        return self.__pulse.current_unfiltered

    def get_signal(self, **kwargs):
        from scipy.signal import unit_impulse
        fs = int(self.__dialog.pulseFs.currentText()[0:2]) * 1000
        samples = unit_impulse(4 * fs, 'mid')
        signal = Signal(self.__dialog.pulsePrefix.text(), samples, self.__prefs, fs=fs)
        return SingleChannelSignalData(name=signal.name, signal=signal)


class SignalDialog(QDialog, Ui_addSignalDialog):
    '''
    Alows user to extract a signal from a wav or frd.
    '''

    def __init__(self, preferences, signal_model, allow_multichannel=True, parent=None):
        super(SignalDialog, self).__init__(parent=parent)
        self.setupUi(self)
        self.statusBar = QStatusBar()
        self.verticalLayout.addWidget(self.statusBar)
        self.wavFilePicker.setIcon(qta.icon('fa5s.folder-open'))
        self.frdAvgFilePicker.setIcon(qta.icon('fa5s.folder-open'))
        self.frdPeakFilePicker.setIcon(qta.icon('fa5s.folder-open'))
        self.applyTimeRangeButton.setIcon(qta.icon('fa5s.cut'))
        self.applyTimeRangeButton.setEnabled(False)
        self.__preferences = preferences
        pulse_loader = PulseLoader(self, preferences)
        self.__loaders = [
            DialogWavLoaderBridge(self, preferences, allow_multichannel=allow_multichannel),
            FrdLoader(self),
            pulse_loader
        ]
        self.__loader_idx = self.signalTypeTabs.currentIndex()
        self.__magnitudeModel = MagnitudeModel('preview', self.previewChart, preferences, self.get_curve_data, 'Signal')
        self.__signal_model = signal_model
        if self.__signal_model is None:
            self.filterSelectLabel.setEnabled(False)
            self.filterSelect.setEnabled(False)
            self.linkedSignal.setEnabled(False)
        elif len(self.__signal_model) == 0:
            if len(self.__signal_model.default_signal.filter) > 0:
                self.filterSelect.addItem('Default')
            else:
                self.filterSelectLabel.setEnabled(False)
                self.filterSelect.setEnabled(False)
                self.linkedSignal.setEnabled(False)
        else:
            for s in self.__signal_model:
                if s.master is None:
                    self.filterSelect.addItem(s.name)
        self.clear_signal(draw=False)

    def changeLoader(self, idx):
        self.__loader_idx = idx
        self.__loaders[self.__loader_idx].enable_ok()
        self.__magnitudeModel.redraw()

    def selectFile(self):
        '''
        Presents a file picker for selecting a wav file that contains a signal.
        '''
        self.__loaders[self.__loader_idx].select_wav_file()
        self.enableOk()
        self.__magnitudeModel.redraw()

    def selectPeakFile(self):
        '''
        Presents a file picker for selecting a frd file that contains the peak signal.
        '''
        self.__loaders[self.__loader_idx].select_peak_file()
        self.__magnitudeModel.redraw()

    def selectAvgFile(self):
        '''
        Presents a file picker for selecting a frd file that contains the avg signal.
        '''
        self.__loaders[self.__loader_idx].select_avg_file()
        self.__magnitudeModel.redraw()

    def clear_signal(self, draw=True):
        ''' clears the current signal '''
        self.__loaders[self.__loader_idx].clear_signal()
        if draw:
            self.__magnitudeModel.redraw()

    def reject(self):
        ''' ensure signals are released from memory after we close the dialog '''
        self.__clear_down()
        super().reject()

    def __clear_down(self):
        for l in self.__loaders:
            try:
                l.clear_signal()
            except:
                pass

    def enableLimitTimeRangeButton(self):
        ''' enables the button whenever the time range changes. '''
        self.applyTimeRangeButton.setEnabled(True)
        self.statusBar.showMessage('Click the scissors button to change the slice of the source file to analyse', 8000)
        self.enableOk()

    def limitTimeRange(self):
        ''' changes the applied time range. '''
        self.previewChannel(self.wavChannelSelector.currentText())
        self.applyTimeRangeButton.setEnabled(False)
        self.statusBar.clearMessage()
        self.enableOk()

    def previewChannel(self, channel_idx):
        '''
        Selects the specified channel.
        :param channel_idx: the channel to display.
        '''
        from app import wait_cursor
        with wait_cursor('Preparing Signal'):
            self.__loaders[self.__loader_idx].init_time_range()
            self.__loaders[self.__loader_idx].prepare_signal(int(channel_idx))
            self.__magnitudeModel.redraw()

    def enableOk(self):
        '''
        Enables the ok button if we can save.
        '''
        self.__loaders[self.__loader_idx].enable_ok()

    def get_curve_data(self, reference=None):
        '''
        :param reference: ignored as we don't expose a normalisation control in this chart.
        :return: the peak and avg spectrum for the currently loaded signal (if any).
        '''
        return self.__loaders[self.__loader_idx].get_magnitude_data()

    def masterFilterChanged(self, idx):
        '''
        enables the linked signal checkbox if we have selected a filter.
        :param idx: the selected index.
        '''
        self.linkedSignal.setEnabled(idx > 0)

    def accept(self):
        '''
        Adds the signal to the model and exits if we have a signal (which we should because the button is disabled
        until we do).
        '''
        loader = self.__loaders[self.__loader_idx]
        if loader.can_save():
            from app import wait_cursor
            with wait_cursor(f"Saving signals"):
                signal = loader.get_signal(offset=self.gainOffset.value())
                if signal is not None:
                    self.save(signal)
                    QDialog.accept(self)
                else:
                    logger.warning(f"No signals produced by loader")
            self.__clear_down()

    def save(self, signal):
        ''' saves the specified signals in the signal model'''
        if self.__preferences.get(DISPLAY_SMOOTH_PRECALC):
            QThreadPool.globalInstance().start(Smoother(signal))
        selected_filter_idx = self.filterSelect.currentIndex()
        if selected_filter_idx > 0:  # 0 because the dropdown has a None value first
            if self.filterSelect.currentText() == 'Default':
                self.__apply_default_filter(signal)
            else:
                master = self.__signal_model[selected_filter_idx - 1]
                if isinstance(signal, BassManagedSignalData):
                    for s in signal.channels:
                        self.__copy_filter(master, s)
                else:
                    self.__copy_filter(master, signal)
        self.__signal_model.add(signal)

    def __copy_filter(self, master, signal):
        if self.linkedSignal.isChecked():
            master.enslave(signal)
        else:
            signal.filter = master.filter.resample(signal.fs)

    def __apply_default_filter(self, signal):
        '''
        Copies forward the default filter, using the 1st generated signal as the master if the user has chosen to link
        them.
        :param signal: the signal.
        '''
        if self.linkedSignal.isChecked():
            master = None
            for idx, s in enumerate(signal):
                if idx == 0:
                    s.filter = self.__signal_model.default_signal.filter.resample(s.fs)
                    master = s
                else:
                    master.enslave(s)
        else:
            for s in signal:
                s.filter = self.__signal_model.default_signal.filter.resample(s.fs)

    def toggleDecimate(self, state):
        ''' toggles whether to decimate '''
        if self.wavChannelSelector.count() > 0:
            from app import wait_cursor
            with (wait_cursor()):
                self.__loaders[self.__loader_idx].toggle_decimate(int(self.wavChannelSelector.currentText()))
                self.__magnitudeModel.redraw()


def read_wav_data(input_file, start=None, end=None):
    '''
    Reads a wav file and returns the raw samples
    :param input_file: the file to read.
    :param start: the start point, if none then read from the start.
    :param end: the end point, if none then read to the end.
    :return: the samples, fs and metadata
    '''
    import soundfile as sf
    info = sf.info(input_file)
    max_frames = math.floor(0x1000000 / info.channels)
    if start is not None or end is not None:
        start_frame = 0 if start is None else int(start * (info.samplerate / 1000))
        end_frame = None if end is None else int(end * (info.samplerate / 1000))
        frames_to_read = end_frame - start_frame
        if info.format.upper() == 'FLAC' and frames_to_read > max_frames:
            ys, frame_rate = __read_flac_in_chunks(input_file, max_frames, start_frame, end_frame)
        else:
            ys, frame_rate = sf.read(input_file, start=start_frame, stop=end_frame, always_2d=True)
    else:
        if info.format.upper() == 'FLAC' and info.frames > max_frames:
            ys, frame_rate = __read_flac_in_chunks(input_file, max_frames, 0, info.frames)
        else:
            ys, frame_rate = sf.read(input_file, always_2d=True)
    return ys, frame_rate, {SIGNAL_SOURCE_FILE: input_file, SIGNAL_START: start, SIGNAL_END: end}


def __read_flac_in_chunks(input_file, max_frames, start_frame, end_frame):
    '''
    Workaround for https://github.com/erikd/libsndfile/issues/431 by reading the flac in chunks.
    :param input_file: the input file.
    :param max_frames: the frames to read in one chunk.
    :param start_frame: the first frame to read.
    :param end_frame: the last frame to read.
    :return: data, frame_rate array.
    '''
    import soundfile as sf
    dats = []
    read_end_frame = start_frame
    while read_end_frame < end_frame:
        read_end_frame = min(start_frame + max_frames, end_frame)
        logger.info(f"Loading {input_file} chunk from {start_frame} to {read_end_frame}")
        ys, frame_rate = sf.read(input_file, start=start_frame, stop=read_end_frame, always_2d=True)
        dats.append(ys)
        start_frame = read_end_frame
    ys = np.concatenate(dats)
    logger.info(f"Loaded {input_file} {ys.shape} ")
    return ys, frame_rate


def readWav(name, preferences, input_file=None, input_data=None, channel=1, start=None, end=None, target_fs=1000,
            offset=0.0) -> Signal:
    """ reads a wav file or data from a wav file into Signal, one of input_file or input_data must be provided.
    :param name: the name of the signal.
    :param input_file: a path to the input signal file
    :param input_data: data read using readWav.
    :param channel: the channel to read.
    :param start: the time to start reading from in ms
    :param end: the time to end reading from in ms.
    :param target_fs: the fs of the Signal to return (resampling if necessary)
    :returns: Signal.
    """
    if input_data is None and input_file is not None:
        ys, fs, metadata = read_wav_data(input_file, start=start, end=end)
    elif input_data is not None and input_file is None:
        ys, fs, metadata = input_data
    else:
        raise ValueError('must supply one of input_file or input_data')
    signal = Signal(name, ys[:, channel - 1], preferences, fs=fs, metadata={**metadata, SIGNAL_CHANNEL: channel})
    if target_fs is None or target_fs == 0:
        target_fs = signal.fs
    return signal.resample(target_fs).offset(offset)


class Smoother(QRunnable):
    fractions = [0, 1, 2, 3, 6, 12, 24]

    '''
    Precalculates the fractional octave smoothing.
    '''

    def __init__(self, signal_data):
        super().__init__()
        self.__signal_data = signal_data

    def run(self):
        if isinstance(self.__signal_data, BassManagedSignalData):
            for c in self.__signal_data.channels:
                QThreadPool.globalInstance().start(Smoother(c))
        else:
            self.__smooth(self.__signal_data)

    def __smooth(self, signal_data):
        for fraction in self.fractions:
            start = time.time()
            signal_data.smooth(fraction, set_active=False)
            end = time.time()
            logger.info(f"Smoothed {signal_data} at {fraction} in {round(end - start, 3)}s")


def get_visible_signal_name_filter(show_filtered_signals, show_signals):
    '''
    Creates a regex that will filter the signal names according to the avg/peak patterns.
    :param show_filtered_signals: which filtered signals to show.
    :param show_signals: which signals to show.
    :return: the pattern (if any)
    '''
    analysis_types = []
    if show_signals in SHOWING_AVERAGE:
        analysis_types.append('avg')
    if show_signals in SHOWING_PEAK:
        analysis_types.append('peak')
    if show_signals in SHOWING_MEDIAN:
        analysis_types.append('median')
    analysis_match = '|'.join(analysis_types)
    if show_filtered_signals == SHOW_FILTERED_ONLY:
        filter_match = '-filtered'
    elif show_filtered_signals == SHOW_UNFILTERED_ONLY:
        filter_match = ''
    else:
        filter_match = '(-filtered)?'
    return re.compile(f".*_({analysis_match}){filter_match}$")


class MergeSignalDialog(QDialog, Ui_MergeSignalDialog):
    '''
    Alows user to merge multiple signals.
    '''

    def __init__(self, preferences, signal_model: SignalModel, parent=None):
        super(MergeSignalDialog, self).__init__(parent=parent)
        self.setupUi(self)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.__prefs = preferences
        self.__signal_model = signal_model
        single_signals = {s.name: s for s in self.__signal_model.non_bm_signals if s.signal is not None}
        bm_signals = {c.name: c for bm in [bm.channels for bm in self.__signal_model.bass_managed_signals] for c in bm}
        self.__signals: Dict[str, SingleChannelSignalData] = {**single_signals, **bm_signals}
        for s in self.__signals.keys():
            self.signals.addItem(s)
        self.__validate()

    def __validate(self):
        self.buttonBox.button(QDialogButtonBox.Save).setEnabled(len(self.signals.selectedItems()) > 0)

    def calc_duration(self):
        duration = 0
        if len(self.signals.selectedItems()) > 0:
            duration = sum([self.__signals[s.text()].duration_seconds for s in self.signals.selectedItems()])
        self.duration.setTime(QtCore.QTime(0, 0, 0).addMSecs(int(duration * 1000)))
        self.__validate()

    def accept(self):
        selected_signals: List[Signal] = [self.__signals[s.text()].signal for s in self.signals.selectedItems()]
        logger.debug(f"Merging {','.join([s.name for s in selected_signals])}")
        samples = np.concatenate([s.samples for s in selected_signals])
        suffix = f"{len([s.name for s in self.__signal_model.non_bm_signals if s.name.startswith('merged')]) + 1}"
        output_signal = Signal(f"merged{suffix}", samples, self.__prefs, selected_signals[0].fs)
        self.__signal_model.add(SingleChannelSignalData(f"merged{suffix}", signal=output_signal,
                                                        filter=CompleteFilter(fs=output_signal.fs)))
        super().accept()
