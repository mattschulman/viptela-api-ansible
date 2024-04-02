#!/usr/bin/python
_metaclass_ = type
DOCUMENTATION = r'''
---
module: viptela_api_set_default_version.py
short_description: A module to generate a HTTP POST Body and then send the POST to a vManage host to start an set-default job.
version_added: "0.0.1"
description: A module to generate a HTTP POST Body and then send the POST to a vManage host to start an set-default job.
options:
    vmanage:
        description: target vManage device ip/dnsName
        required: true
        type: str
    cookie:
        description: API Cookie to authenticate to vManage
        required: true
        type: str
    token:
        description: XSRF Token to authenticate to vManage
        required: true
        type: str
    device_list:
        description: list of device dictionaries to obtain the info for the POST body.
        required: true
        type: str
    debug:
        description: detailed debug on module lvl with using print statements
        required: false
        type: bool
author:
    - Matt Schulman
Example playbook setup:
  - name: Set Default Version on vEdge
    viptela_api_set_default_version:
      vmanage: "{{ ansible_host }}"
      cookie: "{{ login_result.set_cookie }}"
      token: "{{ token_result.content }}"
      device_list: "{{ validatedDeviceDictList }}"
    register: setDefault_result
  - debug: var=setDefault_result.last_status
'''
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
  def __init__(self, vmanage, cookie, token, device_list, debug = False):
    self.vmanage = vmanage
    self.cookie = cookie
    self.token = token
    # self.version = version
    self.device_list = device_list
    self.statusCode = 0
    self.setDefaultID = ""

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
  
  def setDefaultVersion(self):
    ''' Connect to vManage and set a version as default on a vEdge'''

    self.print_debug(" -- upload: ", "", 1)
    self.print_debug(" -- vmanage: ", self.vmanage, 1)
    self.print_debug(" -- cookie: ", self.cookie, 1)
    self.print_debug(" -- token: ",self.token, 1)
    # self.print_debug(" -- version: ", self.version, 1)

    urllib3.disable_warnings()

    url = 'https://' + self.vmanage + '/dataservice/device/action/defaultpartition'
    self.print_debug(" -- url: ", url, 1)



    # Create the payload structure as a dictionary.  The devices list will be appended in a for loop later.
    payloadDict = {
       'action': 'defaultpartition',
       'devices': [],
       'deviceType': 'vedge'
    }

    #Generate the devices key as a list of device IPs and device IDs if the inputted version matches the version for this API call
    for device in self.device_list:
      # if device['version'] == self.version:
      setDefaultDeviceDict = {
        'version': self.__normalize_version(device['version']),
        'deviceIP': device['systemIP'],
        'deviceId': device['deviceID']
      }
      payloadDict['devices'].append(setDefaultDeviceDict)

    headers = {
       'X-XSRF-TOKEN': self.token,
       'Cookie': self.cookie,
       'Content-Type': 'application/json'
    }

    self.print_debug("  -- headers: ", headers, 1)
    self.print_debug("  -- payload: ", headers, 1)

    response = requests.request('POST', url, headers=headers, data=json.dumps(payloadDict), verify=False)

    self.print_debug("  -- status_text: ", response.text, 1)
    self.print_debug("  -- status_code: ", response.status_code, 1)
    self.statusCode = str(response.status_code)

    # Convert the unicode response to a dictionary using ast to get the id key
    ansi_response = ast.literal_eval(response.text)
    self.setDefaultID = ansi_response['id']
    self.print_debug("  -- setDefaultID: ", self.setDefaultID, 1)

    if response.status_code == 200:
       return True
    else:
       return False
  
  def __normalize_version(self, version):
    ''' On IOS-XE versions convert the version to the first 5 fields only'''
    normalized_version = ""
    version_list = version.split('.')
    normalized_version_list = []
    # IOS-XE version string - take only the first 5 fields
    if len(version_list) > 5:
      normalized_version_list = version_list[:5]
    # Viptela-OS version string - use the whole string
    else:
      normalized_version_list = version_list

    normalized_version = '.'.join(normalized_version_list)
    return normalized_version
  
# Main
def main():
  ''' Main funciton whih will be executed by playbook (or for in standalone python run) '''

  # Definition of input structure (arguments)
  module_args = {
    "vmanage": { "type": 'str', "required": True },
    "cookie": { "type": 'str', "required": True },
    "token": { "type": 'str', "required": True },
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
    module.params['device_list'],
    module.params['debug']
  )

  viptelaSession.print_debug("-- viptela-setDefaultVersion: ", "", 1)
  if module.check_mode:
    module.exit_json(**viptelaSession.result)
  
   # do action + output structure enrichment and evaluation
  if viptelaSession.setDefaultVersion():
    viptelaSession.result["last_status"] = viptelaSession.setDefaultID
    viptelaSession.result['changed'] = True       
  else:
    viptelaSession.result["stdout_lines"] = viptelaSession.setDefaultID
    module.fail_json(msg='viptela Code Set-Default error.  Check last_status', **viptelaSession.result)

  # Return output structure
  module.exit_json(**viptelaSession.result)

if __name__ == "__main__":
  main()