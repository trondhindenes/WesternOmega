# Western Omega

An acl proxy for Elasticsearch

## ACL description
### Policies
A _Policy_ is attached to an _entity_ using a _mapping_.
A Policy describes a set of allowed/disallowed operations against an Elasticsearch cluster,
such as "allow searches in indexes A, B but not C". 

You can have multiple mappings, in a single file or multiple. The filename of all mappings file must start with "mapping".
WesternOmega currencly supports ip-based authorization along with basic authentication.
When using basic authentication, the users can either be stored in a json file on the file system.
Passwords can be stored either in plaintext or encrypted using base64-encoded pbkdf2_sha256 hashes.

In order to create a hash for a user, you can use the the python script "create_hash.py" in the utils folder of this repo.


#### Operations
List of index-related operations:   
`index:createindex`: Allow creation of an index. Also required for changing index settings  
`index:deleteindex`: Allow deletion of an index      
`index:search`: Allow searches against the index   
`index:msearch` Allow searches using the msearch api against the index   
`index:scroll` Allow searches using the scroll api against the index   
`index:createdocument`: Allow the creation of documents against the index   
`index:deletedocument`: Allow deletion of documents from the index
`index:getsettings`: Get settings for the index
`index:closeindex`: Close the index   
`index:openindex`: Open the index   
`index:getmapping`: Get mappings in the index
`index:mget`: Use the Multi Get API to search

List of cluster-related operations:   
`cluster:base`: Allow ping the es cluster   
`cluster:gethealth`: Allow reading cluster health state   
`cluster:changesettings`: Allow changing cluster settings   
`cluster:scroll`: Allows the use of the scroll API (this ID uses an id to get subsequent pages, 
but the first page requires the `index:search` action, so you should be fairly safe to allow it)
`cluster:getsnapshotrepos`: Allows using the cat api and other apis to list snapshot repos


#### Resources
A policy describes allowed actions against a _resource_.
Resources are specified in the format `<type>:::<name>`.
A type can be either `index` or `cluster`.
As an example, a policy allowing search access to all `logstash` indexes would use 
the resource name `index:::logstash*:*`. The last `*` represents types in the index,   
allowing you to specify acls on a per-type basis. 

## Configuring WesternOmega
The supplied config.yaml file should have fairly sane defaults. You can also use envvars or 
volume mappings in `/run/secrets` to configure them.   
The most important setting is the url of the elasticsearch cluster.

The default config is using Flask's builtin SimpleCache so that the app can be rnu without further ado.
However, it is recommended to use a Redis cache instead, which can be configured by using the "cache_type"   
config setting.


