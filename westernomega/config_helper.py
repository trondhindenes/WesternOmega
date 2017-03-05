import os
import sys
from ConfigParser import SafeConfigParser
import json
import yaml
import dpath

#This is just a helper to find the location of config.ini and parse it
class ConfigHelper(object):

    @staticmethod
    def get_config_path(config_file_name='config.json'):
        here = os.path.dirname(__file__)
        parent = os.path.abspath(os.path.join(here, os.pardir))
        config_file_path = os.path.join(parent, config_file_name)

        if os.path.isfile(config_file_path):
            return config_file_path
        else:
            raise ValueError(str.format("error reading file {0}", config_file_path))

    @staticmethod
    def get_config_variable(config_file, setting_name, format='json', default_value=None, get_env=True):
        file_setting = None
        try_utf_encoding = False
        json_value = None
        try:
            file = open(config_file, "r")
            config_str = file.read()
            file.close()
            if format == 'json':
                config_data = json.loads(str(config_str))
            elif format == 'yaml':
                config_data = yaml.load(str(config_str))
            else:
                raise ValueError("format has to be either json or yaml")
            json_value = dpath.util.get(config_data, setting_name)
        except:
            try_utf_encoding = True

        if try_utf_encoding:
            try:
                config_str = config_str.decode('utf-8-sig')
                config_data = json.loads(config_str)
                json_value = dpath.util.get(config_data, setting_name)
            except:
                pass

        #Test docker secret store
        if os.path.exists(os.path.join('/run/secrets/', setting_name)):
            file = open(os.path.join('/run/secrets/', setting_name), "r")
            value = file.read()
            return value

        #Test env vars
        if os.getenv(setting_name, None):
            return os.getenv(setting_name)
        else:
            if json_value:
                return json_value
            else:
                return None