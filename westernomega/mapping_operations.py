from westernomega import appconfig, cache
from acl import Acl
import requests
import logging
import time

logger = logging.getLogger('WesternOmega')

class MappingOperations(object):
    acl = Acl()
    upstream = appconfig['elasticsearch_upstream_server']

    def base_map_op(self, path, method, request, content=None):
        operation = None

        parts = str(path).split('/')
        if parts[1] == '_mapping':
            if method == 'get':
                operation = 'cluster:getmappings'
            resource = 'cluster'


        if operation and resource:
            logger.info(str.format("WO:mappinghandler: operation:{0}, resource:{1}", operation, resource))
            if self.acl.verify_access(operation, resource, request, cache):
                has_access = True
                start_time = time.time()
                if method == 'get':
                    result = requests.get(self.upstream + request.full_path)
                elif method == 'put':
                    result = requests.put(self.upstream + request.full_path, data=content)
                elif method == 'post':
                    result = requests.post(self.upstream + request.full_path, data=content)
                logger.info(str.format("WO:cathandler upstream execution time:{0} seconds", (time.time() - start_time)))
            else:
                has_access = False
                result = 'Access Denied'
        else:
            has_access = False
            result = 'Access Denied'

        return has_access, result
