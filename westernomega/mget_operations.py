from westernomega import appconfig
from acl import Acl
import requests
import json
import time

class MGetOperations(object):
    acl = Acl()
    upstream = appconfig['elasticsearch_upstream_server']

    def base_mget_op(self, path, method, request, content=None):
        operation = 'index:mget'
        resource = None

        if method == 'post':
            data = request.data
            data_obj = json.loads(data)
            for doc in data_obj['docs']:
                index_name = doc['_index']

            resource = str.format('index:::{0}', index_name)

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
