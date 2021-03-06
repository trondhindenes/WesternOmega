from westernomega import appconfig, cache
from acl import Acl
import requests
import json
import time

class BaseOperations(object):
    acl = Acl()
    upstream = appconfig['elasticsearch_upstream_server']

    def base_base_op(self, path, method, request, content=None):
        operation = 'cluster:base'
        resource = 'cluster'

        if method == 'get':
            if (self.acl.verify_access(operation, resource, request, cache)):
                has_access = True
                result = requests.get(self.upstream + path)
            else:
                has_access = False
                result = None
        return has_access, result
