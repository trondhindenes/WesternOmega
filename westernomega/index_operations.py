from westernomega import appconfig, cache
from acl import Acl
import requests
import logging
import time
from requests_wrapper import esreq

logger = logging.getLogger('WesternOmega')

class IndexOperations(object):
    acl = Acl()
    upstream = appconfig['elasticsearch_upstream_server']

    def base_index_op(self, path, method, request, content=None):
        operation = None
        # split the parts, count them and figure out what api this is
        parts = str(path).split('/')
        resource = str.format('index:::{0}:*', parts[1])

        has_access = False
        if len(parts) == 2:
            # The first part is always junk. If only two parts, look at the method/body to figure out what it is
            if method == 'put':
                operation = 'index:createindex'
            elif method == 'get':
                operation = 'index:getindexsettings'
            elif method == 'delete':
                operation = 'index:deleteindex'

        elif len(parts) == 3:
            # Look at the real) second part, could be either a type or a sub-api
            if parts[2] == '_settings':
                if method == 'get':
                    operation = operation = 'index:getindexsettings'
            elif parts[2] == '_close':
                if method == 'post':
                    operation = operation = 'index:closeindex'
            elif parts[2] == '_open':
                if method == 'post':
                    operation = operation = 'index:openindex'
            elif parts[2] == '_search':
                if method == 'get':
                    operation = 'index:searchindex'
            elif parts[2] == '_mapping':
                if method == 'get':
                    operation = 'index:getmapping'
            else:
                if method == 'post':
                    #insert document using automatic ID generation
                    operation = 'index:createdocument'

        elif len(parts) == 4:
            if parts[2] in ['_close', '_open', '_settings']:
                pass
            elif parts[3] == '_search':
                if method == 'post':
                    #This is a search against a specified type
                    operation = 'index:searchindex'
                    resource = resource + ':' + parts[2]
            else:
                if method == 'get':
                    #this is a specified get using index, type and id
                    operation = 'index:searchindex'
                    resource = resource + ':' + parts[2]
                elif method == 'put':
                    #Insert (index) doc using index, type and id
                    operation = 'index:createdocument'
                    resource = resource + ':' + parts[2]
                elif method == 'post':
                    operation = 'index:createdocument'

        elif len(parts) == 5:
            if parts[2] in ['_close', '_open', '_settings']:
                pass
            elif parts[2] == '_mapping':
                if method == 'get':
                    operation = 'index:getmapping'
            elif parts[3] == '_search':
                if method == 'post':
                    pass
            elif parts[4] == '_create':
                if method == 'post':
                    operation = 'index:createdocument'
            elif parts[4] == '_update':
                if method == 'post':
                    operation = 'index:updatedocument'

        elif len(parts) == 6:
            if parts[2] in ['_mapping']:
                if method == 'get':
                    operation = 'index:getmapping'
                    resource = str.format('index:::{0}:{1}', parts[1], parts[3])



        if operation and resource:
            logger.info(str.format("WO:Indexhandler: operation:{0}, resource:{1}", operation, resource))
            if self.acl.verify_access(operation, resource, request, cache):
                has_access = True
                start_time = time.time()

                logger.debug(str.format('WO:Indexhandler content:'))
                logger.debug(request.data)
                logger.debug(str.format('WO:Indexhandler content-type:'))
                if 'content-type' in request.headers:
                    logger.debug(request.headers['content-type'])

                if method == 'get':
                    result = esreq(self.upstream, 'get', request)
                if method == 'delete':
                    result = esreq(self.upstream, 'delete', request)
                elif method == 'put':
                    result = esreq(self.upstream, 'put', request)
                elif method == 'post':
                    logger.debug(content)
                    result = esreq(self.upstream, 'post', request)
                logger.info(str.format("WO:Indexhandler upstream execution time:{0} seconds", (time.time() - start_time)))
            else:
                has_access = False
                result = 'Access Denied'
        else:
            has_access = False
            result = 'Access Denied'

        return has_access, result