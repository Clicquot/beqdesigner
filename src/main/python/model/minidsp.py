import glob
import logging
import os
import shutil
from pathlib import Path

import qtawesome as qta
from qtpy.QtCore import QObject, Signal, QRunnable, QThreadPool, Qt, QDateTime
from qtpy.QtWidgets import QDialog, QFileDialog, QMessageBox

from model.iir import Passthrough, PeakingEQ, Shelf, LowShelf, HighShelf
from model.preferences import BEQ_CONFIG_FILE, BEQ_MERGE_DIR, BEQ_MINIDSP_TYPE, BEQ_DOWNLOAD_DIR, BEQ_EXTRA_DIR
from ui.minidsp import Ui_mergeMinidspDialog

logger = logging.getLogger('minidsp')

BMILLER_GITHUB_MINIDSP = 'https://github.com/bmiller/miniDSPBEQ'
BMILLER_MINI_DSPBEQ_GIT_REPO = f"{BMILLER_GITHUB_MINIDSP}.git"


class MergeFiltersDialog(QDialog, Ui_mergeMinidspDialog):
    '''
    Save Chart dialog
    '''

    def __init__(self, parent, prefs, statusbar):
        super(MergeFiltersDialog, self).__init__(parent)
        self.setupUi(self)
        self.__process_spinner = None
        self.configFilePicker.setIcon(qta.icon('fa5s.folder-open'))
        self.outputDirectoryPicker.setIcon(qta.icon('fa5s.folder-open'))
        self.processFiles.setIcon(qta.icon('fa5s.save'))
        self.refreshGitRepo.setIcon(qta.icon('fa5s.sync'))
        self.userSourceDirPicker.setIcon(qta.icon('fa5s.folder-open'))
        self.clearUserSourceDir.setIcon(qta.icon('fa5s.times', color='red'))
        self.__preferences = prefs
        self.statusbar = statusbar
        config_file = self.__preferences.get(BEQ_CONFIG_FILE)
        if config_file is not None and len(config_file) > 0 and os.path.exists(config_file):
            self.configFile.setText(os.path.abspath(config_file))
        self.outputDirectory.setText(self.__preferences.get(BEQ_MERGE_DIR))
        os.makedirs(self.outputDirectory.text(), exist_ok=True)
        minidsp_type = self.__preferences.get(BEQ_MINIDSP_TYPE)
        if minidsp_type is not None and len(minidsp_type) > 0:
            self.minidspType.setCurrentText(minidsp_type)
        self.__beq_dir = self.__preferences.get(BEQ_DOWNLOAD_DIR)
        extra_dir = self.__preferences.get(BEQ_EXTRA_DIR)
        if extra_dir is not None and len(extra_dir) > 0 and os.path.exists(extra_dir):
            self.userSourceDir.setText(os.path.abspath(extra_dir))
        self.__update_beq_metadata()
        self.__enable_process()

    def refresh_repo(self):
        from app import wait_cursor
        with wait_cursor():
            RepoRefresher(self.__beq_dir).refresh()
            self.__update_beq_metadata()

    def __update_beq_metadata(self):
        git_files = 0
        user_files = 0
        if os.path.exists(self.__beq_dir) and os.path.exists(os.path.join(self.__beq_dir, '.git')):
            git_files = len(glob.glob(f"{self.__beq_dir}{os.sep}**{os.sep}*.xml", recursive=True))
            self.__load_repo_metadata()
        else:
            self.__beq_dir_not_exists()

        if len(self.userSourceDir.text().strip()) > 0 and os.path.exists(self.userSourceDir.text()):
            user_files = len(glob.glob(f"{self.userSourceDir.text()}{os.sep}**{os.sep}*.xml", recursive=True))

        if user_files > 0 or git_files > 0:
            self.__show_or_hide(git_files > 0, user_files > 0)
            self.totalFiles.setValue(user_files + git_files)

    def __load_repo_metadata(self):
        from dulwich import porcelain
        try:
            with porcelain.open_repo_closing(self.__beq_dir) as local_repo:
                last_commit = local_repo[local_repo.head()]
                last_commit_time_utc = last_commit.commit_time
                last_commit_qdt = QDateTime()
                last_commit_qdt.setTime_t(last_commit_time_utc)
                self.lastCommitDate.setDateTime(last_commit_qdt)
                from datetime import datetime
                import calendar
                d = datetime.utcnow()
                now_utc = calendar.timegm(d.utctimetuple())
                days_since_commit = (now_utc - last_commit_time_utc) / 60 / 60 / 24
                warning_msg = ''
                if days_since_commit > 7.0:
                    warning_msg = f"&nbsp;was {round(days_since_commit)} days ago, press the button to update -->"
                commit_link = f"{BMILLER_GITHUB_MINIDSP}/commit/{last_commit.id.decode('utf-8')}"
                self.infoLabel.setText(f"<a href=\"{commit_link}\">Last Commit</a>{warning_msg}")
                self.infoLabel.setTextFormat(Qt.RichText)
                self.infoLabel.setTextInteractionFlags(Qt.TextBrowserInteraction)
                self.infoLabel.setOpenExternalLinks(True)
                self.lastCommitMessage.setPlainText(
                    f"Author: {last_commit.author.decode('utf-8')}\n\n{last_commit.message.decode('utf-8')}")
        except:
            logger.exception(f"Unable to open git repo in {self.__beq_dir}")
            self.__beq_dir_not_exists()

    def __beq_dir_not_exists(self):
        self.infoLabel.setText(
            f"BEQ Filter repo not found at {self.__beq_dir}, press the button to clone the repository -->")

    def __show_or_hide(self, has_git_files, has_user_files):
        self.lastCommitDate.setVisible(has_git_files)
        has_any_files = has_git_files or has_user_files
        self.totalFiles.setVisible(has_any_files)
        self.lastCommitMessage.setVisible(has_git_files)
        self.lastUpdateLabel.setVisible(has_git_files)
        self.filesProcessed.setVisible(has_any_files)
        self.filesProcessedLabel.setVisible(has_any_files)
        self.ofLabel.setVisible(has_any_files)
        self.minidspType.setVisible(has_any_files)
        self.minidspTypeLabel.setVisible(has_any_files)
        self.processFiles.setVisible(has_any_files)
        self.errors.setVisible(has_any_files)
        self.errorsLabel.setVisible(has_any_files)

    def process_files(self):
        '''
        Creates the output content.
        '''
        self.__preferences.set(BEQ_CONFIG_FILE, self.configFile.text())
        self.__preferences.set(BEQ_MERGE_DIR, self.outputDirectory.text())
        self.__preferences.set(BEQ_MINIDSP_TYPE, self.minidspType.currentText())
        self.__preferences.set(BEQ_EXTRA_DIR, self.userSourceDir.text())
        self.__update_beq_metadata()
        if self.__clear_output_directory():
            self.filesProcessed.setValue(0)
            self.__start_spinning()
            self.errors.clear()
            self.errors.setEnabled(False)
            QThreadPool.globalInstance().start(XmlProcessor(self.__beq_dir,
                                                            self.userSourceDir.text(),
                                                            self.outputDirectory.text(),
                                                            self.configFile.text(),
                                                            self.minidspType.currentText(),
                                                            self.__on_file_fail,
                                                            self.__on_file_ok,
                                                            self.__on_complete))

    def __on_file_fail(self, file, message):
        self.errors.setEnabled(True)
        self.errors.addItem(f"{file} - {message}")

    def __on_file_ok(self):
        self.filesProcessed.setValue(self.filesProcessed.value()+1)

    def __on_complete(self):
        self.__stop_spinning()

    def __stop_spinning(self):
        from model.batch import stop_spinner
        stop_spinner(self.__process_spinner, self.processFiles)
        self.__process_spinner = None
        self.processFiles.setIcon(qta.icon('fa5s.save'))
        self.processFiles.setEnabled(True)

    def __start_spinning(self):
        self.__process_spinner = qta.Spin(self.processFiles)
        spin_icon = qta.icon('fa5s.spinner', color='green', animation=self.__process_spinner)
        self.processFiles.setIcon(spin_icon)
        self.processFiles.setEnabled(False)

    def __clear_output_directory(self):
        '''
        Empties the output directory if required
        '''
        import glob
        matching_files = glob.glob(f"{self.outputDirectory.text()}/**/*.xml", recursive=True)
        if len(matching_files) > 0:
            result = QMessageBox.question(self,
                                          'Clear Directory',
                                          f"All XML files will be deleted from {self.outputDirectory.text()}\nAre you sure you want to continue?",
                                          QMessageBox.Yes | QMessageBox.No,
                                          QMessageBox.No)
            if result == QMessageBox.Yes:
                for file in matching_files:
                    self.statusbar.showMessage(f"Deleting {file}", 2000)
                    os.remove(file)
                    self.statusbar.showMessage(f"Deleted {file}", 2000)
                self.statusbar.showMessage(f"Cleared {len(matching_files)} XML files from {self.outputDirectory.text()}", 5000)
                return True
            else:
                return False
        else:
            return True

    def pick_output_dir(self):
        '''
        Sets the output directory.
        '''
        dialog = QFileDialog(parent=self)
        dialog.setFileMode(QFileDialog.DirectoryOnly)
        dialog.setOption(QFileDialog.ShowDirsOnly)
        dialog.setWindowTitle('Select a location to store the generated minidsp config files')
        if dialog.exec():
            selected = dialog.selectedFiles()
            if len(selected) > 0:
                if os.path.abspath(selected[0]) == os.path.abspath(self.__beq_dir):
                    QMessageBox.critical(self, '',
                                         f"Output directory cannot be inside the input directory, choose a different folder",
                                         QMessageBox.Ok)
                else:
                    abspath = os.path.abspath(f"{selected[0]}{os.path.sep}beq_minidsp")
                    if not os.path.exists(abspath):
                        try:
                            os.mkdir(abspath)
                        except:
                            QMessageBox.critical(self, '', f"Unable to create directory - {abspath}", QMessageBox.Ok)
                    if os.path.exists(abspath):
                        self.outputDirectory.setText(abspath)
        self.__enable_process()

    def clear_user_source_dir(self):
        self.userSourceDir.clear()
        self.__update_beq_metadata()

    def pick_user_source_dir(self):
        '''
        Sets the user source directory.
        '''
        dialog = QFileDialog(parent=self)
        dialog.setFileMode(QFileDialog.DirectoryOnly)
        dialog.setOption(QFileDialog.ShowDirsOnly)
        dialog.setWindowTitle('Choose a directory which holds your own BEQ files')
        if dialog.exec():
            selected = dialog.selectedFiles()
            if len(selected) > 0:
                if os.path.abspath(selected[0]) == os.path.abspath(self.__beq_dir):
                    QMessageBox.critical(self, '',
                                         f"User directory cannot be inside the input directory, choose a different folder",
                                         QMessageBox.Ok)
                else:
                    self.userSourceDir.setText(selected[0])
                    self.__update_beq_metadata()

    def pick_config_file(self):
        '''
        Picks the master config file.
        :return: the file.
        '''
        kwargs = {}
        if self.configFile.text() is not None and len(self.configFile.text()) > 0:
            kwargs['directory'] = str(Path(self.configFile.text()).parent.resolve())
        selected = QFileDialog.getOpenFileName(parent=self, caption='Select Minidsp XML Filter',
                                               filter='Filter (*.xml)', **kwargs)
        if selected is not None and len(selected[0]) > 0:
            self.configFile.setText(os.path.abspath(selected[0]))
        self.__enable_process()

    def __enable_process(self):
        '''
        Enables the process button if we're ready to go.
        '''
        enable = os.path.exists(self.configFile.text()) and os.path.exists(self.outputDirectory.text())
        self.processFiles.setEnabled(enable)


class ProcessSignals(QObject):
    on_failure = Signal(str, str)
    on_success = Signal()
    on_complete = Signal()


class XmlProcessor(QRunnable):
    '''
    Completes the batch conversion of minidsp files in a separate thread.
    '''
    def __init__(self, beq_dir, user_source_dir, output_dir, config_file, minidsp_type, failure_handler, success_handler, complete_handler):
        super().__init__()
        self.__beq_dir = beq_dir
        self.__user_source_dir = user_source_dir
        self.__output_dir = output_dir
        self.__config_file = config_file
        self.__parser = TwoByFourXmlParser() if minidsp_type == '2x4' else HDXmlParser(minidsp_type)
        self.__target_fs = get_minidsp_fs(minidsp_type)
        self.__filters_required = get_filters_required(minidsp_type)
        self.__signals = ProcessSignals()
        self.__signals.on_failure.connect(failure_handler)
        self.__signals.on_success.connect(success_handler)
        self.__signals.on_complete.connect(complete_handler)

    def run(self):
        self.__process_dir(self.__beq_dir)
        self.__process_dir(self.__user_source_dir)
        self.__signals.on_complete.emit()

    def __process_dir(self, src_dir):
        if len(src_dir) > 0:
            beq_dir = Path(src_dir)
            base_parts_idx = len(beq_dir.parts)
            for xml in beq_dir.glob(f"**{os.sep}*.xml"):
                self.__process_file(base_parts_idx, xml)

    def __process_file(self, base_parts_idx, xml):
        '''
        Processes an individual file.
        :param base_parts_idx: the path index to start from.
        :param xml: the source xml.
        '''
        try:
            dir_parts = xml.parts[base_parts_idx:-1]
            file_output_dir = os.path.join(self.__output_dir, *dir_parts)
            os.makedirs(file_output_dir, exist_ok=True)
            dst = Path(file_output_dir).joinpath(xml.name)
            logger.info(f"Copying {self.__config_file} to {dst}")
            dst = shutil.copy2(self.__config_file, dst.resolve())
            filters = extract_and_pad_with_passthrough(str(xml),
                                                       fs=self.__target_fs,
                                                       required=self.__filters_required)
            output_xml = self.__parser.overwrite(filters, dst)
            with dst.open('w') as dst_file:
                dst_file.write(output_xml)
            self.__signals.on_success.emit()
        except Exception as e:
            logger.exception(f"Unexpected failure during processing of {xml}")
            self.__signals.on_failure.emit(xml.name, str(e))


class TwoByFourXmlParser:
    '''
    Handles the 2x4 model
    '''
    def overwrite(self, filters, target):
        import xml.etree.ElementTree as ET
        import re
        logger.info(f"Copying {len(filters)} to {target}")
        et_tree = ET.parse(str(target))
        root = et_tree.getroot()
        filter_matcher = re.compile('^EQ_ch([1-2])_1_([1-6])$')
        bq_matcher = re.compile('^EQ_ch([1-2])_1_([1-6])_([A-B][0-2])$')
        for child in root:
            if child.tag == 'filter':
                filter_name = child.attrib['name']
                matches = filter_matcher.match(filter_name)
                if matches is not None and len(matches.groups()) == 2:
                    filt_slot = matches.group(2)
                    if int(filt_slot) > len(filters):
                        root.remove(child)
                    else:
                        filt = filters[int(filt_slot) - 1]
                        if isinstance(filt, Passthrough):
                            child.find('freq').text = '1000'
                            child.find('q').text = '1'
                            child.find('gain').text = '0'
                            child.find('boost').text = '0'
                            child.find('type').text = 'PK'
                            child.find('bypass').text = '1'
                            child.find('basic').text = 'true'
                        else:
                            child.find('freq').text = str(filt.freq)
                            child.find('q').text = str(filt.q)
                            child.find('boost').text = str(filt.gain)
                            child.find('type').text = get_minidsp_filter_code(filt)
                            child.find('bypass').text = '0'
                            child.find('basic').text = 'true'
            elif child.tag == 'item':
                filter_name = child.attrib['name']
                matches = bq_matcher.match(filter_name)
                if matches is not None and len(matches.groups()) == 3:
                    filt_slot = matches.group(2)
                    biquad_coeff = matches.group(3)
                    if int(filt_slot) > len(filters):
                        root.remove(child)
                    else:
                        filt = filters[int(filt_slot) - 1]
                        if isinstance(filt, Passthrough):
                            child.find('dec').text = '0'
                            child.find('hex').text = '00800000' if biquad_coeff == 'B0' else '00800000'
                        else:
                            child.find('dec').text = '0'
                            hex_txt = filt.format_biquads(True, separator=',', show_index=True, to_hex=True,
                                                          fixed_point=True)[0]
                            hex_val = dict(item.split("=") for item in hex_txt.split(','))[biquad_coeff.lower()]
                            child.find('hex').text = hex_val

        return ET.tostring(root, encoding='unicode')


class HDXmlParser:
    '''
    Handles HD models (2x4HD and 10x10HD)
    '''
    def __init__(self, minidsp_type):
        self.__minidsp_type = minidsp_type

    def overwrite(self, filters, target, metadata=None):
        '''
        Overwrites the PEQ_1_x and PEQ_2_x filters.
        :param filters: the filters.
        :param target: the target file.
        :return: the xml to output to the file.
        '''
        import xml.etree.ElementTree as ET
        logger.info(f"Copying {len(filters)} to {target}")
        et_tree = ET.parse(str(target))
        root = et_tree.getroot()
        for child in root:
            if child.tag == 'filter':
                if 'name' in child.attrib:
                    filter_tokens = child.attrib['name'].split('_')
                    (filt_type, filt_channel, filt_slot) = filter_tokens
                    if len(filter_tokens) == 3:
                        if filt_type == 'PEQ':
                            if filt_channel in self.__valid_filt_channels():
                                if int(filt_slot) > len(filters):
                                    root.remove(child)
                                else:
                                    filt = filters[int(filt_slot)-1]
                                    if isinstance(filt, Passthrough):
                                        child.find('freq').text = '1000'
                                        child.find('q').text = '0.7'
                                        child.find('boost').text = '0'
                                        child.find('type').text = 'PK'
                                        child.find('bypass').text = '1'
                                    else:
                                        child.find('freq').text = str(filt.freq)
                                        child.find('q').text = str(filt.q)
                                        child.find('boost').text = str(filt.gain)
                                        child.find('type').text = get_minidsp_filter_code(filt)
                                        child.find('bypass').text = '0'
                                    dec_txt = filt.format_biquads(True, separator=',',
                                                                  show_index=False, to_hex=False)[0]
                                    child.find('dec').text = f"{dec_txt},"
                                    hex_txt = filt.format_biquads(True, separator=',',
                                                                  show_index=False, to_hex=True,
                                                                  fixed_point=self.__is_fixed_point_hardware())[0]
                                    child.find('hex').text = f"{hex_txt},"
        if metadata:
            metadata_tag = ET.Element('beq_metadata')
            for key, value in metadata.items():
                tag = ET.Element(key)

                if type(value) is list:
                    for item in value:
                        sub_tag = ET.Element('value')
                        sub_tag.text = item
                        tag.append(sub_tag)
                else:
                    tag.text = metadata[key]
                metadata_tag.append(tag)

            root.append(metadata_tag)

        return ET.tostring(root, encoding='unicode')

    def __is_fixed_point_hardware(self):
        return False if self.__minidsp_type == '2x4 HD' else True

    def __valid_filt_channels(self):
        '''
        :return: list of valid channels.
        '''
        return [str(x) for x in range(11, 21)] if self.__minidsp_type == '10x10 HD' else ['1', '2']


def get_filters_required(minidsp_type):
    '''
    :return: the fs for the selected minidsp.
    '''
    return 10 if minidsp_type == '2x4 HD' else 6


def get_minidsp_fs(minidsp_type):
    '''
    :return: the fs for the selected minidsp.
    '''
    return 96000 if minidsp_type == '2x4 HD' else 48000


def get_minidsp_filter_code(filt):
    '''
    :param filt: the filter.
    :return: the string filter type for a minidsp xml.
    '''
    if isinstance(filt, PeakingEQ):
        return 'PK'
    elif isinstance(filt, LowShelf):
        return 'SL'
    elif isinstance(filt, HighShelf):
        return 'SH'
    else:
        raise ValueError(f"Unknown minidsp filter type {type(filt)}")


def xml_to_filt(file, fs=1000):
    ''' Extracts a set of filters from the provided minidsp file '''
    from model.iir import PeakingEQ, LowShelf, HighShelf

    filts = __extract_filters(file)
    output = []
    for filt_tup, count in filts.items():
        filt_dict = dict(filt_tup)
        if filt_dict['type'] == 'SL':
            filt = LowShelf(fs, float(filt_dict['freq']), float(filt_dict['q']), float(filt_dict['boost']),
                            count=count)
            output.append(filt)
        elif filt_dict['type'] == 'SH':
            filt = HighShelf(fs, float(filt_dict['freq']), float(filt_dict['q']), float(filt_dict['boost']),
                             count=count)
            output.append(filt)
        elif filt_dict['type'] == 'PK':
            for i in range(0, count):
                filt = PeakingEQ(fs, float(filt_dict['freq']), float(filt_dict['q']), float(filt_dict['boost']))
                output.append(filt)
        else:
            logger.info(f"Ignoring unknown filter type {filt_dict}")
    return output


def __extract_filters(file):
    import xml.etree.ElementTree as ET
    from collections import Counter

    ignore_vals = ['hex', 'dec']
    tree = ET.parse(file)
    root = tree.getroot()
    filts = {}
    for child in root:
        if child.tag == 'filter':
            if 'name' in child.attrib:
                current_filt = None
                filter_tokens = child.attrib['name'].split('_')
                (filt_type, filt_channel, filt_slot) = filter_tokens
                if len(filter_tokens) == 3:
                    if filt_type == 'PEQ':
                        if filt_channel not in filts:
                            filts[filt_channel] = {}
                        filt = filts[filt_channel]
                        if filt_slot not in filt:
                            filt[filt_slot] = {}
                        current_filt = filt[filt_slot]
                        for val in child:
                            if val.tag not in ignore_vals:
                                current_filt[val.tag] = val.text
                if current_filt is not None:
                    if 'bypass' in current_filt and current_filt['bypass'] == '1':
                        del filts[filt_channel][filt_slot]
                    elif 'boost' in current_filt and current_filt['boost'] == '0':
                        del filts[filt_channel][filt_slot]
    final_filt = None
    # if 1 and 2 are identical then throw one away
    if '1' in filts and '2' in filts:
        filt_1 = filts['1']
        filt_2 = filts['2']
        if filt_1 == filt_2:
            final_filt = list(filt_1.values())
        else:
            raise ValueError(f"Different input filters found in {file} - Input 1: {filt_1} - Input 2: {filt_2}")
    elif '1' in filts:
        final_filt = list(filts['1'].values())
    elif '2' in filts:
        final_filt = list(filts['2'].values())
    else:
        if len(filts.keys()) == 1:
            for k in filts.keys():
                final_filt = filts[k]
        else:
            raise ValueError(f"Multiple active filters found in {file} - {filts}")
    if final_filt is None:
        raise ValueError(f"No filters found in {file}")
    return Counter([tuple(f.items()) for f in final_filt])


def extract_and_pad_with_passthrough(filt_xml, fs, required=10):
    '''
    Extracts the filters from the XML and pads with passthrough filters.
    :param filt_xml: the xml file.
    :param fs: the target fs.
    :param required: how many filters do we need.
    :return: the filters.
    '''
    return pad_with_passthrough(xml_to_filt(filt_xml, fs=fs), fs, required)


def pad_with_passthrough(filters, fs, required):
    flattened_filters = []
    for filt in filters:
        if isinstance(filt, PeakingEQ):
            flattened_filters.append(filt)
        elif isinstance(filt, Shelf):
            flattened_filters.extend(filt.flatten())
    padding = required - len(flattened_filters)
    if padding > 0:
        pad_filters = [Passthrough(fs=fs)] * padding
        flattened_filters.extend(pad_filters)
    elif padding < 0:
        raise ValueError(f"BEQ has too many filters for device (remove {abs(padding)} biquads)")
    return flattened_filters


class RepoRefresher:

    def __init__(self, repo_dir):
        self.repo_dir = repo_dir

    def refresh(self):
        ''' Pulls or clones the named repository '''
        from app import wait_cursor
        with wait_cursor():
            os.makedirs(self.repo_dir, exist_ok=True)
            git_metadata_dir = os.path.abspath(os.path.join(self.repo_dir, '.git'))
            if os.path.exists(git_metadata_dir):
                from dulwich.errors import NotGitRepository
                try:
                    self.__pull_beq()
                except NotGitRepository as e:
                    logger.exception('.git exists but is not a git repo, attempting to delete .git directory and clone')
                    os.rmdir(git_metadata_dir)
                    self.__clone_beq()
            else:
                self.__clone_beq()

    def __pull_beq(self):
        ''' pulls the git repo but does not use dulwich pull as it has file lock issues hon windows '''
        from dulwich import porcelain, index
        with porcelain.open_repo_closing(self.repo_dir) as local_repo:
            remote_refs = porcelain.fetch(local_repo, BMILLER_MINI_DSPBEQ_GIT_REPO)
            local_repo[b"HEAD"] = remote_refs[b"refs/heads/master"]
            index_file = local_repo.index_path()
            tree = local_repo[b"HEAD"].tree
            index.build_index_from_tree(local_repo.path, index_file, local_repo.object_store, tree)

    def __clone_beq(self):
        ''' clones the git repo '''
        from dulwich import porcelain
        porcelain.clone(BMILLER_MINI_DSPBEQ_GIT_REPO, self.repo_dir, checkout=True)
