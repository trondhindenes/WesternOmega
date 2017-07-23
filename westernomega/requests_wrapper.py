import requests
import logging
import json

#logger = logging.getLogger('WesternOmega')

def esreq(upstream_url, method, original_request):
    headers = {}
    if 'content-type' in original_request.headers:
        orig_content_type = original_request.headers['content-type']

        headers['Content-Type'] = str(orig_content_type)

    result = None

    url = upstream_url + str(original_request.path)
    if original_request.query_string != '':
        url = url + '?' + original_request.query_string
    content = original_request.data

    req = {
        'url': url,
        'headers': headers
    }
    if content == '':
        content = None

    else:
        req['data'] = content

    if method == 'get':
        result = requests.get(**req)
    elif method == 'delete':
        result = requests.delete(**req)
    elif method == 'post':
        result = requests.post(**req)
    elif method == 'put':
        result = requests.put(**req)
    return result