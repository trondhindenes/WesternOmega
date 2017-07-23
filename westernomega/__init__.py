import os
import sys
import json
import log

from ConfigParser import SafeConfigParser
from flask import render_template
from flask import Flask, request, render_template, session, flash, redirect, url_for, jsonify
from flask_restful import Resource, Api, reqparse, fields
from flask_cors import CORS, cross_origin
from werkzeug.contrib.cache import SimpleCache, RedisCache
import werkzeug
from functools import wraps
from config_helper import ConfigHelper
#from flask_restful_swagger import swagger


this_path = sys.path[0]

#current dir
cwd = os.getcwd()
#current dir
here = os.path.dirname(__file__)

static_files_path = os.path.join(here, 'static')
app = Flask(__name__, static_folder=static_files_path)


config = ConfigHelper.get_config_path('config.yaml')
appconfig = {}
appconfig['elasticsearch_upstream_server'] = ConfigHelper.get_config_variable(config,
                                                                      'elasticsearch_backend_host', format='yaml')
appconfig['acl_config_folder'] = ConfigHelper.get_config_variable(config, 'acl_config_folder', format='yaml')
appconfig['logging_level'] = ConfigHelper.get_config_variable(config, 'logging_level', format='yaml')
appconfig['cache_type'] = ConfigHelper.get_config_variable(config, 'cache_type', format='yaml')
appconfig['redis_host'] = ConfigHelper.get_config_variable(config, 'redis_host', format='yaml')
appconfig['redis_port'] = ConfigHelper.get_config_variable(config, 'redis_port', format='yaml')
appconfig['redis_db'] = ConfigHelper.get_config_variable(config, 'redis_db', format='yaml')
appconfig['mappings'] = {}
appconfig['policies'] = {}

logger = log.setup_custom_logger(appconfig['logging_level'])

if appconfig['cache_type'].lower() == 'redis':
    cache = RedisCache(host=appconfig['redis_host'], port=appconfig['redis_port'])
else:
    cache = SimpleCache()


api = Api(app)

import westernomega.api_endpoint
