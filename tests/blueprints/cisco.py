import logging
import traceback
import sys
from netmiko import ConnectHandler
from ciscoconfparse import CiscoConfParse
from optparse import OptionParser
from cloudify.state import ctx_parameters as inputs

extra_cmds = []


###############################################################################
# Parse script params
def processGlobal(option, opt, value, parser):
  setattr(parser.values, option.dest, value.split(';'))
def processParentWithChild(option, opt, value, parser):
  regex_list =  value.split(';')
  setattr(parser.values, option.dest, dict(zip(regex_list[0::2], regex_list[1::2])))

parser = OptionParser()
parser.add_option("-c", "--cmds_file",
                  dest="cmds_file",
                  help="Commands file that will be appended after cleanup")
parser.add_option("-s", "--server_host",
                  dest="host",
                  help="Host IP address")
parser.add_option("-p", "--port",
                  dest="port",
                  default=22,
                  help="Host target port. Default: 22")
parser.add_option("-u", "--login_user",
                  dest="user",
                  default="",
                  help="Login user name")
parser.add_option("-l", "--login_password",
                  dest="password",
                  default="",
                  help="Password for login")
parser.add_option("-e", "--enable_password",
                  dest="enable_password",
                  default="",
                  help="Password for enable command")
parser.add_option('-r', '--retries',
                  dest='retries',
                  default=3,
                  help="Specify number of connection retries. Default: 3")
parser.add_option("-d", "--dry_run",
                  dest="dry_run",
                  action='count',
                  help="Perform dry run. Log the commands but do not send them to the device")
parser.add_option("-i", "--input_config",
                  dest="input_config",
                  help="Use provided configuration file (as running-config) instead of device")
parser.add_option("-t", "--telnet",
                  dest="telnet",
                  action='count',
                  help="Use telnet protocol. Default is to use SSH")
parser.add_option('-v', '--verbose',
                  dest='verbose',
                  action='count',
                  help="Increase verbosity level (use -vv for DEBUG level)")
parser.add_option('-x', '--remove_global',
                  type='string',
                  action='callback',
                  dest = 'remove_global',
                  default=[],
                  callback=processGlobal,
                  help="Global configuration commands to remove. Separated by semicolon. Example: ^ip nat;^ip vrf")
parser.add_option('-y', '--remove_children_from_parent',
                  type='string',
                  action='callback',
                  dest='remove_children_from_parent',
                  callback=processParentWithChild,
                  default={},
                  help="Global parent nodes with specific children pairs to remove (separated by semicolon). Pairs are also separated by semicolon. Example: ^interface;ip nat;^interface;ip address")

(script_opts, args) = parser.parse_args()


if __name__ == '__main__':
  setattr(parser.values, 'host', inputs.get('host', ''))
  setattr(parser.values, 'user', inputs.get('user', ''))
  setattr(parser.values, 'password', inputs.get('password', ''))
  setattr(parser.values, 'enable_password', inputs.get('enable_password',''))
  setattr(parser.values, 'remove_global', inputs.get('remove_global', '').split(';'))
  r = inputs.get('remove_children_from_parent', '')
  r = r.split(';')
  setattr(parser.values, 'remove_children_from_parent', dict(zip(r[0::2], r[1::2])))
  setattr(parser.values, 'telnet', 1 if inputs.get('telnet', False) else 0)
  setattr(parser.values, 'dry_run', 1 if inputs.get('dry_run', False) else 0 )
  extra_cmds = inputs.get('extra_cmds', '').split(';')



if not (script_opts.host or script_opts.input_config):
    parser.error('Host address or input file is mandatory')
if script_opts.host and script_opts.input_config:
    parser.error('Host address and input file options are exclusive')

###############################################################################
# Setup loggers
log_level = logging.WARNING
if script_opts.verbose == 1:
    log_level = logging.INFO
elif script_opts.verbose >= 2:
    log_level = logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)

###############################################################################
# Classes
class ConfigProvider(object):
    '''
        Base class for configuration provider
    '''
    def __init__(self, config, logger):
        self.original_config = CiscoConfParse(config)
        self.modified_config = CiscoConfParse(config)
        self.logger = logger
    def updateConfig(self, extra_cmds):
        pass
    def getConfigDiffToRemove(self):
        return self.original_config.req_cfgspec_excl_diff(".*", ".*", self.modified_config.ioscfg)
    def removeGlobal(self, global_config_regex):
        for line in self.modified_config.find_objects(global_config_regex):
            line.delete(False)
    def removeParentWithChild(self, parent_config_regex, child_config_regex):
        for parent in self.modified_config.find_objects(parent_config_regex):
            parent.delete_children_matching(child_config_regex)
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

class CiscoConfigProvider(ConfigProvider):
    '''
        Connects to a Cisco device retrieves and updates config
    '''
    def __init__(self, connection_config, logger):
        self.logger = logger
        self.logger.debug("Connecting to device")
        self.net_connect = ConnectHandler(**connection_config)
        self.logger.debug("Entering privileged mode")
        self.net_connect.enable()
        self.logger.debug("Retrieving running configuration")
        config = self.net_connect.send_command('show run').splitlines()
        super(CiscoConfigProvider, self).__init__(config, logger)
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.debug("Closing connection")
        self.net_connect.disconnect()
    def updateConfig(self, extra_cmds=[]):
        all_cmds = []
        all_cmds.extend(self.getConfigDiffToRemove())
        all_cmds.extend(extra_cmds)
        self.logger.debug("\n".join(all_cmds))
        if not self.net_connect:
            raise Exception("Cannot send configuration. Not connected to the device")
        self.logger.debug("Sending commands to the device")
        self.net_connect.send_config_set(all_cmds)

class CiscoConfigProviderRo(CiscoConfigProvider):
    '''
        Read-only Cisco configuration provider
    '''
    def updateConfig(self, extra_cmds=[]):
        all_cmds = []
        all_cmds.extend(self.getConfigDiffToRemove())
        all_cmds.extend(extra_cmds)
        self.logger.info("\n".join(all_cmds))


class FileConfigProvider(ConfigProvider):
    '''
        File configuration provider
    '''
    def __init__(self, file, logger):
        config = []
        with open(script_opts.input_config, 'r') as file:
            config = [line.rstrip() for line in file]
        super(FileConfigProvider, self).__init__(config, logger)
    def updateConfig(self, extra_cmds=[]):
        all_cmds = []
        all_cmds.extend(self.getConfigDiffToRemove())
        all_cmds.extend(extra_cmds)
        self.logger.info("\n".join(all_cmds))

###############################################################################
# Global variables
attempt = 1;
cisco_ios = {
    "device_type": "cisco_ios_telnet" if script_opts.telnet else "cisco_ios",
    "ip": script_opts.host,
    "username": script_opts.user,
    "password": script_opts.password,
    "secret": script_opts.enable_password}
###############################################################################
# Main loop
while attempt < int(script_opts.retries):
    try:
        if script_opts.input_config:
            configProvider = FileConfigProvider(script_opts.input_config, logger)
        else:
            if script_opts.dry_run:
                configProvider = CiscoConfigProviderRo(cisco_ios, logger)
            else:
                configProvider = CiscoConfigProvider(cisco_ios, logger)

        with configProvider as confInterf:

            for parent in script_opts.remove_children_from_parent:
                child = script_opts.remove_children_from_parent[parent]
                if len(parent) > 0 and len(child) > 0:
                  configProvider.removeParentWithChild(parent, child)
            for remove_global in script_opts.remove_global:
                if len(remove_global) > 0:
                  configProvider.removeGlobal(remove_global)

            # Add configuration lines from file
            # extra_cmds = []
            # if script_opts.cmds_file:
                # with open(script_opts.cmds_file, 'r') as cmdsfile:
                    # extra_cmds = [line.rstrip() for line in cmdsfile]

            configProvider.updateConfig(extra_cmds)
        break
    except Exception as e:
        attempt = attempt + 1
        if attempt < script_opts.retries:
            logger.warning("Could not complete tasks for: {}. Exception: {}. Attempt {} of {}. Retrying..."
                           .format(str(script_opts.host), str(e), str(attempt), str(script_opts.retries)))
        else:
            logger.error("Could not complete tasks for: {}. Exception: {} All {} attempts failed"
                         .format(str(script_opts.host), str(e), str(script_opts.retries)))
        logger.debug(traceback.format_exc())
