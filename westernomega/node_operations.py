from westernomega import appconfig
from acl import Acl
import requests
import logging
import time

logger = logging.getLogger('WesternOmega')

class NodesOperations(object):
    acl = Acl()
    upstream = appconfig['elasticsearch_upstream_server']

    def base_nodes_op(self, path, method, request, content=None):
        operation = None
        # split the parts, count them and figure out what api this is
        parts = str(path).split('/')
        resource = 'nodes:::*'

        has_access = False
        if len(parts) == 2:
            # The first part is always junk. If only two parts, look at the method/body to figure out what it is
            if method == 'get':
                operation = 'nodes:getsettings'
        elif len(parts) == 3:
            # The first part is always junk. If only two parts, look at the method/body to figure out what it is
            resource = str.format('nodes:::{0}', parts[2])
            if method == 'get':
                operation = 'nodes:getsettings'

        if operation and resource:
            logger.info(str.format("WO:Indexhandler: operation:{0}, resource:{1}", operation, resource))
            if (self.acl.verify_access(operation, resource, request)):
                has_access = True
                start_time = time.time()
                if method == 'get':
                    result = requests.get(self.upstream + request.full_path)
                elif method == 'put':
                    result = requests.put(self.upstream + request.full_path, data=content)
                elif method == 'post':
                    result = requests.post(self.upstream + request.full_path, data=content)
                logger.info(str.format("WO:Indexhandler upstream execution time:{0} seconds", (time.time() - start_time)))
            else:
                has_access = False
                result = 'Access Denied'
        else:
            has_access = False
            result = 'Access Denied'

        return has_access, result