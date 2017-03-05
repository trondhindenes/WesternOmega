from westernomega import appconfig
from acl import Acl
import requests
import logging
import time

logger = logging.getLogger('WesternOmega')

class ClusterOperations(object):
    acl = Acl()
    upstream = appconfig['elasticsearch_upstream_server']

    def base_cluster_op(self, path, method, request, content=None):
        operation = None
        resource = 'cluster'
        # split the parts, count them and figure out what api this is
        parts = str(path).split('/')

        if parts[2] == 'health':
            operation = 'cluster:gethealth'

        if operation and resource:
            logger.info(str.format("WO:clusterhandler: operation:{0}, resource:{1}", operation, resource))
            if (self.acl.verify_access(operation, resource, request)):
                has_access = True
                start_time = time.time()
                if method == 'get':
                    result = requests.get(self.upstream + request.full_path)
                elif method == 'put':
                    result = requests.put(self.upstream + request.full_path, data=content)
                elif method == 'post':
                    result = requests.post(self.upstream + request.full_path, data=content)
                logger.info(str.format("WO:clusterhandler upstream execution time:{0} seconds", (time.time() - start_time)))
            else:
                has_access = False
                result = 'Access Denied'
        else:
            has_access = False
            result = 'Access Denied'

        return has_access, result
