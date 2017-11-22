import configuration
import sys
import os
from versa_plugin.versaclient import VersaClient
if len(sys.argv) != 2:
    print 'Need file'
    quit()

file_name = sys.argv[1]

if not os.path.isfile(file_name):
    print 'Wrong file'
    quit()

client = VersaClient(configuration.versa_config, '')
for line in open(file_name):
    if line.startswith('nms rbac oauth'):
        token = line.split()[5]
        print token
        client.access_token = token
        client.revoke_token()
