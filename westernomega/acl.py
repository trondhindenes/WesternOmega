from westernomega import appconfig
import json
import fnmatch
from netaddr import IPNetwork, IPAddress

class Acl(object):
    def __init__(self):
        pass

    def match_resource(self, resource, match_resource):
        return fnmatch.fnmatch(resource, match_resource)

    def check_allowed_cidr(self, client_addr, mapping_cidr):
        if IPAddress(client_addr) in IPNetwork(mapping_cidr):
            return True
        else:
            return False

    def verify_access(self, operation, resource, request):
        #Build graph of user's access
        #ip-based access

        #this will hold a list of appliable policies which we can check against.
        #TODO: Cache in redis!!
        applied_policies = []
        for mapping in appconfig['mappings']:
            for mapping_definition in appconfig['mappings'][mapping]['Statement']:
                if mapping_definition['entitytype'] == 'allowedcidr':
                    if self.check_allowed_cidr(request.remote_addr, str(mapping_definition['entitydefinition'])):
                        for policy in mapping_definition['policies']:
                            applied_policies.append(policy)


        matches = []
        for policy in applied_policies:
            for statement in appconfig['policies'][policy]['Statement']:
                if self.match_resource(resource, statement['Resource']):
                    #Resource matches, check operation
                    for action in statement['Action']:
                        if self.match_resource(operation, action):
                            matches.append(statement)

        if len(matches) > 0:
            return True
        else:
            return False