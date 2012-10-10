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

import sys, os, json
from odict import OrderedDict

class Config(dict):
        
    def __init__(self, user_file=None):
        self.config = OrderedDict()
        self.user_file = user_file
        self.update(self.get_running_config())
        
    def set_user_file(self, user_file):
        self.user_file = user_file
        
    def add_category(self, category):
        if not self.config.has_key(category):
            self.config[category] = OrderedDict()
            
    def add_setting(self, category, setting, value, about='', type=0, stub=False, **kwargs):
        assert category != None, 'Must specify a category'
        assert setting != None, 'Must specify a setting'
        assert value != None, 'Must specify a value'
        self.add_category(category)
        if not self.config[category].has_key(setting):
            self.config[category][setting] = OrderedDict()
        self.config[category][setting]['value'] = value
        if not stub:
            self.config[category][setting]['about'] = about
            self.config[category][setting]['type'] = type
            for k in kwargs:
                self.config[category][setting][k] = kwargs[k]
        self.update(self.get_running_config())
        
    def get_setting(self, category, setting, complete=False):
        assert category != None, 'Must specify a category'
        assert setting != None, 'Must specify a setting'
        assert self.config.has_key(category), 'Category does not exist'
        assert self.config[category].has_key(setting), 'Setting in category does not exist'
        assert self.config[category][setting].has_key('value'), 'Setting in category has no value'
        if complete:
            return self.config[category][setting]
        else:
            return self.config[category][setting]['value']
        
    def update_setting_value(self, category, setting, value):
        assert category != None, 'Must specify a category'
        assert setting != None, 'Must specify a setting'
        assert value != None, 'Must specify a value'
        if self.config.has_key(category):
            if self.config[category].has_key(setting):
                self.config[category][setting]['value'] = value
                self.update(self.get_running_config())
    
    def get_settings(self, category):
        assert category != None, 'Must specify a category'
        assert self.config.has_key(category), 'Category does not exist'
        return self.config[category].keys()
    
    def get_categories(self):
        return self.config.keys()
        
    def update_from_string(self, json_config):
        try:
            config = json.loads(json_config)
            for c in config.keys():
                for s in config[c].keys():
                    self.update_setting_value(c, s, config[c][s]['value'])
        except ValueError:
            sys.stderr.write('Empty or malformed config file found!\n')
        
                
    def update_from_user_file(self):
        if self.user_file and os.path.isfile(self.user_file):
            with open(self.user_file, 'r') as f:
                return self.update_from_string(f.read())
            
    def get_running_config(self):
        tmpCfg = {}
        for category in self.config.keys():
            tmpCfg[category] = {}
            for setting in self.config[category].keys():
                tmpCfg[category][setting] = self.config[category][setting]['value']
        return tmpCfg
            
    def __str__(self):
        return json.dumps(self.get_running_config(), separators=(',', ':'), sort_keys=True)        
