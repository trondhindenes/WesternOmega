from westernomega import appconfig
from acl import Acl
import requests
import json
import time

class MSearchOperations(object):
    acl = Acl()
    upstream = appconfig['elasticsearch_upstream_server']

    def base_msearch_op(self, path, method, request, content=None):
        operation = 'index:msearch'
        resource = None

        if method == 'post':
            data = content.splitlines()
            #TODO: We're currently only checking the first index, user could post msearch queries against other indexes
            index_indicator_obj = json.loads(data[0])

            #Support Kibana's inconsistencies
            if type(index_indicator_obj['index']) is list:
                index_name = index_indicator_obj['index'][0]
            elif type(index_indicator_obj['index']) is unicode:
                index_name = index_indicator_obj['index']

            resource = resource = str.format('index:::{0}', index_name)

        if operation and resource:
            if (self.acl.verify_access(operation, resource, request)):
                has_access = True
                if method == 'post':
                    result = requests.post(self.upstream + path, data=content)
            else:
                has_access = False
                result = 'Access Denied'
        else:
            has_access = False
            result = 'Access Denied'

        return has_access, result
