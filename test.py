import esmanagement.elasticsearch_helper
from esmanagement import elasticsearch_helper
import json

es_url = 'http://rtv-test-es05.system.rikstv.no:9200'

success, result_obj = elasticsearch_helper.create_index('test-2017-03', es_url)
print(json.dumps(result_obj))

success, result_obj = elasticsearch_helper.set_index('test-2017-03', es_url, replicas_count=0)
print(json.dumps(result_obj))

success, result_obj = elasticsearch_helper.set_index_node_policy('test-2017-03', es_url, node_policy='whatever')
print(json.dumps(result_obj))

success, result_obj = elasticsearch_helper.set_index_node_policy('test-2017-03', es_url, node_policy='cold')
print(json.dumps(result_obj))