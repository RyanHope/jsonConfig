# -*- coding:    utf-8 -*-
#===============================================================================
# This file is part of jsonConfig.
# Copyright (C) 2012 Ryan Hope <rmh3093@gmail.com>
#
# jsonConfig is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# jsonConfig is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with jsonConfig.  If not, see <http://www.gnu.org/licenses/>.
#===============================================================================

import os, copy, platform, json

from config import Config
import constants

from PySide.QtCore import QObject, SIGNAL, Qt
from PySide.QtGui import QMainWindow, QDoubleSpinBox, QComboBox, QSpinBox, \
    QCheckBox, QLineEdit, QListWidget, QStackedWidget, QSizePolicy, \
    QGridLayout, QScrollArea, QWidget, QVBoxLayout, QLabel, QDialogButtonBox, \
    QHBoxLayout, QDesktopWidget, QMessageBox, QMenuBar, QMenu, QKeySequence, \
    QAction, QFontMetrics

class MyEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__
    
class ComboBox(QComboBox):
    
    def __init__(self, editor, config, category, setting, info):
        super(ComboBox, self).__init__()
        self.editor = editor
        self.config = config
        self.category = category
        self.setting = setting
        self.info = info
        if info.has_key('options'):
            self.addItems(info['options'])
            for i in range(0,len(info['options'])):
                if info['options'][i] == info['value']:
                    self.setCurrentIndex(i)
        QObject.connect(self, SIGNAL('currentIndexChanged(int)'), self.stateChangeHandler)
        
    def updateValue(self, newVal):
        for i in range(0,len(self.info['options'])):
            if self.info['options'][i] == newVal:
                self.setCurrentIndex(i)
            
    def stateChangeHandler(self, newVal):
        for i in range(0,len(self.info['options'])):
            if self.info['options'][i] == self.info['value']:
                self.config.update_setting_value(self.category, self.setting, self.info['options'][newVal])
        self.editor.dirty_check()

class DoubleSpinBox(QDoubleSpinBox):
    
    def __init__(self, editor, config, category, setting, info):
        super(DoubleSpinBox, self).__init__()
        self.editor = editor
        self.config = config
        self.category = category
        self.setting = setting
        self.info = info
        self.setSingleStep(.01)
        self.setMaximum(1000000)
        self.setValue(info['value'])
        QObject.connect(self, SIGNAL('valueChanged(double)'), self.stateChangeHandler)
        
    def updateValue(self, newVal):
        self.setValue(newVal)
            
    def stateChangeHandler(self, newVal):
        self.config.update_setting_value(self.category, self.setting, newVal)
        self.editor.dirty_check()
        
class SpinBox(QSpinBox):
    
    def __init__(self, editor, config, category, setting, info):
        super(SpinBox, self).__init__()
        self.editor = editor
        self.config = config
        self.category = category
        self.setting = setting
        self.info = info
        self.setMaximum(1000000)
        self.setValue(info['value'])
        QObject.connect(self, SIGNAL('valueChanged(int)'), self.stateChangeHandler)
        
    def updateValue(self, newVal):
        self.setValue(newVal)
            
    def stateChangeHandler(self, newVal):
        self.config.update_setting_value(self.category, self.setting, newVal)
        self.editor.dirty_check()
    
class CheckBox(QCheckBox):
    
    def __init__(self, editor, config, category, setting, info):
        super(CheckBox, self).__init__()
        self.editor = editor
        self.config = config
        self.category = category
        self.setting = setting
        self.info = info
        if info['value']:
            self.setCheckState(Qt.Checked)
        else:
            self.setCheckState(Qt.Unchecked)
        QObject.connect(self, SIGNAL('stateChanged(int)'), self.stateChangeHandler)
        
    def updateValue(self, newVal):
        if newVal:
            self.setCheckState(Qt.Checked)
        else:
            self.setCheckState(Qt.Unchecked)
            
    def stateChangeHandler(self, newVal):
        if newVal == Qt.Checked:
            self.config.update_setting_value(self.category, self.setting, True)
        else:
            self.config.update_setting_value(self.category, self.setting, False)
        self.editor.dirty_check()
            
class LineEdit(QLineEdit):
    
    def __init__(self, editor, config, category, setting, info):
        super(LineEdit, self).__init__()
        self.editor = editor
        self.config = config
        self.category = category
        self.setting = setting
        self.info = info
        self.setText(str(info['value']))
        if info.has_key('n'):
            self.setMaxLength(info['n'])
            self.setFixedWidth(info['n']*self.minimumSizeHint().height())
        QObject.connect(self, SIGNAL('textChanged(QString)'), self.stateChangeHandler)
        
    def updateValue(self, newVal):
        self.setText(str(newVal))
            
    def stateChangeHandler(self, newVal):
        self.config.update_setting_value(self.category, self.setting, newVal)
        self.editor.dirty_check()
    
class ConfigEditor(QMainWindow):
    
    def __init__(self, app, cfg, title='Config Editor'):
        super(ConfigEditor, self).__init__()
        
        self.app = app
        self.config = cfg
        self.title = title
        
    def setup(self):
        
        self.dirty = False
        
        self.def_cfg = copy.deepcopy(self.config)
        self.config.update_from_user_file()
        self.base_cfg = copy.deepcopy(self.config)
        
        self.categories = QListWidget()
        #self.categories.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Expanding)
        self.settings = QStackedWidget()
        #self.categories.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Expanding)
        
        QObject.connect(self.categories, SIGNAL('itemSelectionChanged()'), self.category_selected)
        
        self.widget_list = {}
        for cat in self.config.get_categories():
            self.widget_list[cat] = {}
        longest_cat = 0
        for cat in self.config.get_categories():
            if len(cat) > longest_cat:
                longest_cat = len(cat)
            self.categories.addItem(cat)
            settings_layout = QGridLayout()
            r = 0
            c = 0
            for setting in self.config.get_settings(cat):
                info = self.config.get_setting(cat, setting, True)
                s = QWidget()
                s.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)
                sl = QVBoxLayout()
                label = QLabel()
                if info.has_key('alias'):
                    label.setText(info['alias'])
                else:
                    label.setText(setting)
                if info.has_key('about'):
                    label.setToolTip(info['about'])
                sl.addWidget(label)
                if info['type'] == constants.CT_LINEEDIT:
                    w = LineEdit(self, self.config,cat,setting,info)
                elif info['type'] == constants.CT_CHECKBOX:
                    w = CheckBox(self, self.config,cat,setting,info)
                elif info['type'] == constants.CT_SPINBOX:
                    w = SpinBox(self, self.config,cat,setting,info)
                elif info['type'] == constants.CT_DBLSPINBOX:
                    w = DoubleSpinBox(self, self.config,cat,setting,info)
                elif info['type'] == constants.CT_COMBO:
                    w = ComboBox(self, self.config,cat,setting,info)
                w.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)
                self.widget_list[cat][setting] = w
                sl.addWidget(w)
                s.setLayout(sl)
                c = self.config.config[cat].index(setting) % 2
                settings_layout.addWidget(s, r, c)
                if c == 1:
                    r += 1
            settings = QWidget()
            settings.setLayout(settings_layout)
            settings_scroller = QScrollArea()
            settings_scroller.setWidget(settings)
            settings_scroller.setWidgetResizable(True)
            self.settings.addWidget(settings_scroller)
            
        font = self.categories.font()
        fm = QFontMetrics(font)
        self.categories.setMaximumWidth(fm.widthChar('X')*(longest_cat+4))
        
        self.main = QWidget()
        self.main_layout = QVBoxLayout()
        
        self.config_layout = QHBoxLayout()
        self.config_layout.addWidget(self.categories)
        self.config_layout.addWidget(self.settings)
        
        self.mainButtons = QDialogButtonBox(QDialogButtonBox.RestoreDefaults | QDialogButtonBox.Reset | QDialogButtonBox.Apply)
        self.main_apply = self.mainButtons.button(QDialogButtonBox.StandardButton.Apply)
        self.main_reset = self.mainButtons.button(QDialogButtonBox.StandardButton.Reset)
        self.main_defaults = self.mainButtons.button(QDialogButtonBox.StandardButton.LastButton)
        QObject.connect(self.mainButtons, SIGNAL('clicked(QAbstractButton *)'), self.mainbutton_clicked)
        
        self.dirty_check()
        
        self.main_layout.addLayout(self.config_layout)
        self.main_layout.addWidget(self.mainButtons)
        
        self.main.setLayout(self.main_layout)
        
        self.setCentralWidget(self.main)
        self.setWindowTitle(self.title)
        self.setUnifiedTitleAndToolBarOnMac(True)
        
        self.categories.setCurrentItem(self.categories.item(0))
        
        self.menuBar = QMenuBar()
        self.filemenu = QMenu('&File')
        self.quitAction = QAction(self)
        self.quitAction.setText('&Quit')
        if platform.system() != 'Darwin':
            self.quitAction.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_Q))
        QObject.connect(self.quitAction, SIGNAL('triggered()'), self.quitApp)
        self.filemenu.addAction(self.quitAction)
        self.menuBar.addMenu(self.filemenu)
        self.setMenuBar(self.menuBar)
        
        self.show()
        self.activateWindow()
        self.raise_()
        
        self.setMinimumWidth(self.geometry().width()*1.2)
        
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)
        
    def category_selected(self):
        self.settings.setCurrentIndex(self.config.config.index(self.categories.selectedItems()[0].text()))
        
    def mainbutton_clicked(self, button):
        if button == self.main_reset:
            for cat in self.base_cfg.get_categories():
                for setting in self.base_cfg.get_settings(cat):
                    self.widget_list[cat][setting].updateValue(self.base_cfg.get_setting(cat,setting))
        elif button == self.main_defaults:
            for cat in self.def_cfg.get_categories():
                for setting in self.def_cfg.get_settings(cat):
                    self.widget_list[cat][setting].updateValue(self.def_cfg.get_setting(cat,setting))
        elif button == self.main_apply:
            bad_settings = self.validate_settings()
            if bad_settings == []:
                self.save_settings()
                self.main_apply.setEnabled(False)
                self.main_reset.setEnabled(False)
            else:
                msgBox = QMessageBox()
                msgBox.setText("Must fix the following invalid settings before quitting:")
                msgBox.setStandardButtons(QMessageBox.Ok)
                info = ''
                for setting in bad_settings:
                    new = '%s,%s<br>' % setting
                    info = '%s%s' % (info, new)
                msgBox.setInformativeText(info)
                msgBox.exec_()
            
        
    def quitApp(self):
        self.app.closeAllWindows()
        
    def get_changes(self):
        enc = MyEncoder()
        if enc.encode(self.def_cfg.config) == enc.encode(self.config.config):
            return False
        if enc.encode(self.base_cfg.config) != enc.encode(self.config.config):
            newC = Config()
            for c in self.config.config.keys():
                for s in self.config.config[c].keys():
                    if self.config.config[c][s]['value'] != self.def_cfg.config[c][s]['value']:
                        newC.add_setting(c, s, self.config.config[c][s]['value'], stub=True)    
            return json.dumps(newC.config, separators=(',',': '), indent=4, sort_keys=True)
        else:
            return None
        
    def validate_settings(self):
        ret = []
        for cat in self.config.get_categories():
            for setting in self.config.get_settings(cat):
                info = self.config.get_setting(cat, setting, True)
                if info.has_key('validate'):
                    if not info['validate'](info):
                        ret.append((cat,setting))
        return ret
    
    def dirty_check(self):
        if str(self.base_cfg) != str(self.config):
            self.dirty = True
            self.main_apply.setEnabled(True)
            self.main_reset.setEnabled(True)
        else:
            self.dirty = False
            self.main_apply.setEnabled(False)
            self.main_reset.setEnabled(False)
        if str(self.def_cfg) == str(self.config):
            self.main_defaults.setEnabled(False)
        else:
            self.main_defaults.setEnabled(True)
            
    def save_settings(self):
        config = self.get_changes()
        if config == False:
            if os.path.isfile(self.config.user_file):
                os.remove(self.config.user_file)
        elif config != None:
            with open(self.config.user_file, 'w+') as f:
                f.write(config)
        self.base_cfg = copy.deepcopy(self.config)
            
    def closeEvent(self, event=None):
        self.quitApp()
    
