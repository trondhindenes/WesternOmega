from westernomega import appconfig, cache
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

            index_names = []
            for doc in data_obj['docs']:
                index_names.append(doc['_index'])
            index_names = list(set(index_names))
            if len(index_names) == 1:
                index_name = index_names[0]
                #TODO: We should read type from the request instead of assuming the wildcard
                type_name = '*'
            else:
                #Searched for multuple indexes in one mget operation
                #This is rare, but allowed. For simplicity, we require that the user has
                #access to all indexes for this to go thru
                index_name = '*'
                type_name = '*'
            resource = str.format('index:::{0}:{1}', index_name, type_name)

        if operation and resource:
            if self.acl.verify_access(operation, resource, request, cache):
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
