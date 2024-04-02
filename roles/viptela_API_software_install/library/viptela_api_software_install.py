#!/usr/bin/python
import requests
import pprint
import urllib3
import json
import ast
from ansible.module_utils.basic import AnsibleModule

# Class definitions
class ViptelaAPI(object):
  ''' Viptela API Operations'''

  # Public Methods
  def __init__(self, vmanage, cookie, token, version, reboot, device_list, debug = False):
    self.vmanage = vmanage
    self.cookie = cookie
    self.token = token
    self.version = version
    self.device_list = device_list
    self.reboot = reboot
    self.statusCode = 0
    self.installID = ""

    self.debug = {
      "enabled": debug,
      "lvl": 0,
      "debugColor": "\033[96m",
      "textColor": "\033[92m",
      "headerColor": "\033[93m",
    }

    # Definition of output structure
    self.result = {
      "changed": False,
      "last_status": "info: init"
    }

  def print_debug(self, key, value, lvl):
    ''' debug; lvl full = 0, partial = 1, info = 3, header = 4, silent = 5 '''
    if ((lvl == 4 ) or (lvl == 2)) and (self.debug["enabled"]):
        print(self.debug["headerColor"] + key + self.debug["textColor"] + pprint.pformat(value, 4) + "\033[0m")
        return
    if (lvl == 3) and (self.debug["enabled"]):
        print(self.debug["textColor"] + key + self.debug["textColor"] | pprint.pformat(value, 4) + "\033[0m")
        return
    if (lvl >= self.debug["lvl"]) and (self.debug["enabled"]):
        print(self.debug["debugColor"] + "debug: " + key + self.debug["textColor"] + pprint.pformat(value, 4) + "\033[0m")
  
  def softwareInstall(self):
    ''' Connect to vManage and install an inamge on a vEdge'''

    self.print_debug(" -- upload: ", "", 1)
    self.print_debug(" -- vmanage: ", self.vmanage, 1)
    self.print_debug(" -- cookie: ", self.cookie, 1)
    self.print_debug(" -- token: ",self.token, 1)
    self.print_debug(" -- version: ", self.version, 1)
    self.print_debug(" -- reboot: ", self.reboot, 1)
    self.print_debug(" -- device_list: ", self.device_list, 1)

    urllib3.disable_warnings()

    url = 'https://' + self.vmanage + '/dataservice/device/action/install'
    self.print_debug(" -- url: ", url, 1)

    # Create the payload structure as a dictionary.  The devices list will be appended in a for loop later.
    payloadDict = {
       'action': 'install',
       'input': {
          'vEdgeVPN': 0,
          'vSmartVPN': 0,
          'version': self.version,
          'versionType': 'vmanage',
          'reboot': self.reboot,
          'sync': True
       },
       'devices': [],
       'deviceType': 'vedge'
    }

    #Generate the devices key as a list of device IPs and device IDs if the inputted version matches the version for this API call
    for device in self.device_list:
       if device['version'] == self.version:
          installDeviceDict = {
            'deviceIP': device['systemIP'],
            'deviceId': device['deviceID']
          }
          payloadDict['devices'].append(installDeviceDict)

    headers = {
       'X-XSRF-TOKEN': self.token,
       'Cookie': self.cookie,
       'Content-Type': 'application/json'
    }

    self.print_debug("  -- headers: ", headers, 1)
    self.print_debug("  -- payload: ", payloadDict, 1)

    # Send the API call, converting the payloadDict to JSON
    response = requests.request('POST', url, headers=headers, data=json.dumps(payloadDict), verify=False)

    self.print_debug("  -- status_text: ", response.text, 1)
    self.print_debug("  -- status_code: ", response.status_code, 1)
    self.statusCode = str(response.status_code)

    # Convert the unicode response to a dictionary using ast to get the id key
    ansi_response = ast.literal_eval(response.text)
    self.print_debug("  -- ansi_reponse: ",ansi_response,1)
    self.installID = ansi_response['id']
    self.print_debug("  -- installID: ", self.installID, 1)

    if response.status_code == 200:
       return True
    else:
       return False

# Main
def main():
  ''' Main funciton whih will be executed by playbook (or for in standalone python run) '''

  # Definition of input structure (arguments)
  module_args = {
    "vmanage": { "type": 'str', "required": True },
    "cookie": { "type": 'str', "required": True },
    "token": { "type": 'str', "required": True },
    "version": { "type": 'str', "required": True },
    "reboot": { "type": 'bool', "required": True },
    "device_list": { "type": 'list', "required": True},
    "debug": { "type": 'bool', "required": False }
  }

  # Ansible module instance
  module = AnsibleModule(
    argument_spec = module_args,
    supports_check_mode = True
  )   

  # Run
  viptelaSession = ViptelaAPI (
    module.params['vmanage'],
    module.params['cookie'],
    module.params['token'],
    module.params['version'],
    module.params['reboot'],
    module.params['device_list'],
    module.params['debug']
  )

  viptelaSession.print_debug("-- viptela-softwareInstall: ", "", 1)
  if module.check_mode:
    module.exit_json(**viptelaSession.result)
  
   # do action + output structure enrichment and evaluation
  if viptelaSession.softwareInstall():
    viptelaSession.result["last_status"] = viptelaSession.installID
    viptelaSession.result['changed'] = True       
  else:
    viptelaSession.result["stdout_lines"] = viptelaSession.installID
    module.fail_json(msg='viptela Code Install error.  Check last_status', **viptelaSession.result)

  # Return output structure
  module.exit_json(**viptelaSession.result)

if __name__ == "__main__":
  main()