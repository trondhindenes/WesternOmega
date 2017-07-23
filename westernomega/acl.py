import os
from westernomega import appconfig, cache
import json
import fnmatch
from netaddr import IPNetwork, IPAddress
import logging
import base64
from passlib.hash import pbkdf2_sha256

logger = logging.getLogger('WesternOmega')

class Acl(object):
    def __init__(self):
        self.mapping = {}
        self.policies = {}

    def get_acl_file_info(self):
        mappings = cache.get('mappings')
        policies = cache.get('policies')
        if mappings is None:
            all_mappings = {}
            all_policies = {}
            # Load all mapping and policy files
            here = os.path.dirname(__file__)
            parent = os.path.abspath(os.path.join(here, os.pardir))
            acl_folder = os.path.join(parent, appconfig['acl_config_folder'])
            acl_files = os.listdir(acl_folder)
            for file in acl_files:
                if file.startswith('mapping'):
                    logger.debug('parsing mapping file ' + file)
                    with open((os.path.join(acl_folder, file)), 'r') as f:
                        mapping_obj = json.loads(f.read())
                        all_mappings[file] = mapping_obj
                if file.startswith('policy'):
                    logger.debug('parsing policy file ' + file)
                    with open((os.path.join(acl_folder, file)), 'r') as f:
                        mapping_obj = json.loads(f.read())
                        self.policies[file] = mapping_obj
                        all_policies[file] = mapping_obj
            cache.set('mappings', all_mappings, 300)
            cache.set('policies', all_policies, 300)
            mappings = all_mappings
            policies = all_policies
        return mappings, policies

    def match_resource(self, resource, match_resource):
        return fnmatch.fnmatch(resource, match_resource)

    def check_allowed_cidr(self, client_addr, mapping_cidr):
        if IPAddress(client_addr) in IPNetwork(mapping_cidr):
            return True
        else:
            return False

    def verify_password(self, password, match_password, encryption):
        if encryption == "none":
            if password == match_password:
                return True
        if encryption == 'base64-pbkdf2_sha256':
            password = base64.b64decode(password)
            if pbkdf2_sha256.verify(match_password, password):
                return True

        return False

    def read_storepath_file(self, file_path, cache=None):
        cache_obj_name = 'userlist_'+ file_path
        logger.debug('reading cache object: '+ cache_obj_name)
        try:
            userlist_obj = cache.get(cache_obj_name)

        except:
            logger.warning("Unable to read cache object " + cache_obj_name)
            userlist_obj = None

        if userlist_obj is None:
            try:
                with open(file_path, 'r') as f:
                    logger.debug('Reading basic auth storepath file ' + file_path)
                    userlist_obj = json.loads(f.read())
            except:
                logger.error('Failure Reading basic auth storepath file ' + file_path)
                raise IOError
            logger.debug('storing item in cache: ' + cache_obj_name)
            cache.set(cache_obj_name, userlist_obj, 300)
        return userlist_obj

    def check_basicauth(self, request, entityconfiguration, cache=None):
        username = None
        password = None

        if request.authorization and 'username' in request.authorization and 'password' in request.authorization:
            username = request.authorization['username']
            password = request.authorization['password']
        else:
            return False

        if entityconfiguration['store'] == 'file':
            userlist_obj = self.read_storepath_file(entityconfiguration['storepath'], cache)
            if userlist_obj is None:
                logger.error("Could not find file specified in storeconfig: " + entityconfiguration['storepath'])
                return False

            this_user = [x for x in userlist_obj if x['username'] == username]
            if this_user:
                if self.verify_password(this_user[0]['password'], password, entityconfiguration['encryption']):
                    logger.debug("Passwords match for user " + username)
                    return True
                else:
                    logger.warning("Wrong password for user " + username)
            else:
                return False

            return False

    def verify_access(self, operation, resource, request, cache=None):
        #Build graph of user's access
        #ip-based access

        mappings, policies = self.get_acl_file_info()

        applied_policies = []
        for mapping in mappings:
            for mapping_definition in mappings[mapping]['Statement']:
                if mapping_definition['entitytype'] == 'allowedcidr':
                    if self.check_allowed_cidr(request.remote_addr, str(mapping_definition['entitydefinition'])):
                        for policy in mapping_definition['policies']:
                            applied_policies.append(policy)
                elif mapping_definition['entitytype'] == 'basicauth':
                    if self.check_basicauth(request, mapping_definition['entityconfiguration'], cache):
                        for policy in mapping_definition['policies']:
                            applied_policies.append(policy)



        matches = []
        #unique-ify applied policies in case of doubles
        applied_policies = list(set(applied_policies))

        for policy in applied_policies:
            for statement in policies[policy]['Statement']:
                if self.match_resource(resource, statement['Resource']):
                    #Resource matches, check operation
                    for action in statement['Action']:
                        if self.match_resource(operation, action):
                            matches.append(statement)

        if len(matches) > 0:
            return True
        else:
            return False