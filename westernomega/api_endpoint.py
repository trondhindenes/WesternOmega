from flask_restful import Resource, Api, abort, reqparse
from westernomega import api, app, appconfig, cache
from cluster_operations import ClusterOperations
from index_operations import IndexOperations
from flask import make_response, jsonify, abort, request
from msearch_operations import MSearchOperations
from base_operations import BaseOperations
from node_operations import NodesOperations
from mget_operations import MGetOperations
from cat_operations import CatOperations
from mapping_operations import MappingOperations
import logging
import time
import werkzeug

logger = logging.getLogger('WesternOmega')

class Endpoint(Resource):
    cu = ClusterOperations()
    ci = IndexOperations()
    mi = MSearchOperations()
    cb = BaseOperations()
    no = NodesOperations()
    mg = MGetOperations()
    ct = CatOperations()
    mp = MappingOperations()

    def process_request(self, path, method, request, data=None):
        start_time = time.time()
        logger.info('------------------------------------------------')
        logger.info('Incoming request path: ' + path)
        logger.info(str.format("WO:apiendpoint: path:{0}, method:{1}", path, method))
        result = None
        has_access = False
        op_type = None
        if path.startswith('/_msearch'):
            op_type = 'msearch'
        elif path.startswith('/_mget'):
            op_type = 'mget'
        elif path.startswith('/_nodes'):
            op_type = 'nodes'
        elif path.startswith('/_cluster'):
            op_type = 'cluster'
        elif path.startswith('/_cat'):
            op_type = 'cat'
        elif path.startswith('/_mapping'):
            op_type = 'mapping'
        elif path.startswith('/_aliases'):
            op_type = 'aliases'
        elif path == '/':
            op_type = 'base'
        elif path.startswith('/_') or path.startswith('/-') or path.startswith('/+'):
            op_type = None
        else:
            op_type = 'index'

        if op_type == 'base':
            has_access, result = self.cb.base_base_op(path, method, request, data)
        elif op_type == 'cluster':
            has_access, result = self.cu.base_cluster_op(path, method, request, data)
        elif op_type == 'nodes':
            has_access, result = self.no.base_nodes_op(path, method, request, data)
        elif op_type == 'index':
            has_access, result = self.ci.base_index_op(path, method, request, data)
        elif op_type == 'msearch':
            has_access, result = self.mi.base_msearch_op(path, method, request, data)
        elif op_type == 'mget':
            has_access, result = self.mg.base_mget_op(path, method, request, data)
        elif op_type == 'cat':
            has_access, result = self.ct.base_cat_op(path, method, request, data)
        elif op_type == 'mapping':
            has_access, result = self.mp.base_map_op(path, method, request, data)
        elif op_type == 'aliases':
            #TODO: Implement the alias endpoint
            logger.error('non-implemented endpoint!!!')
            class MyResult():
                pass
            my_result = MyResult()
            my_result.status_code = 999
            has_access, result = True, my_result

        if has_access:
            logger.info(str.format("WO:apiendpoint OperationType:{0}, Access granted:{1}, upstream result:{2}"
                        , op_type, str(has_access), str(result.status_code)))
        else:
            #logger.warning(str.format("WO:apiendpoint OperationType:{0}, Access granted:{1},
            # upstream result:{2}" ,op_type, str(has_access), 0))
            logger.warning(str.format("Access denied: path: {0}, method: {1}", path, method))
        logger.info(str.format("WO:apiendpoint execution time:{0} seconds (including upstream)",
                               (time.time() - start_time)))
        return has_access, result

    def get(self, path=None):
        path = request.path
        method = request.method
        has_access, result = self.process_request(path, 'get', request)
        if has_access:
            resp = make_response()
            resp.status_code = result.status_code
            resp.data = result.content
            resp.headers['content-type'] = result.headers['content-type']
            return resp
        else:
            abort(403)

    def delete(self, path=None):
        path = request.path
        method = request.method
        has_access, result = self.process_request(path, 'delete', request)
        if has_access:
            resp = make_response()
            resp.status_code = result.status_code
            resp.data = result.content
            resp.headers['content-type'] = result.headers['content-type']
            return resp
        else:
            abort(403)

    def put(self, path=None):
        path = request.path
        method = request.method
        request.get_data()
        data = request.data
        has_access, result = self.process_request(path, 'put', request, data)
        if has_access:
            resp = make_response()
            resp.status_code = result.status_code
            resp.data = result.content
            resp.headers['content-type'] = result.headers['content-type']
            return resp
        else:
            abort(403)

    def post(self, path=None):
        path = request.path
        method = request.method
        request.get_data()
        data = request.data
        has_access, result = self.process_request(path, 'post', request, data)
        if has_access:
            resp = make_response()
            resp.status_code = result.status_code
            resp.data = result.content
            resp.headers['content-type'] = result.headers['content-type']
            return resp
        else:
            abort(403)

api.add_resource(Endpoint, '/<path:path>', '/')
