#!/usr/bin/python
_metaclass_ = type
DOCUMENTATION = r'''
---
module: viptela_api_activate_version.py
short_description: A module to generate a HTTP POST Body and then send the POST to a vManage host to start an image upload job.
version_added: "0.0.1"
description: A module to generate a HTTP POST Body and then send the POST to a vManage host to start an image upload job.
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
    srcPath:
        description: path to the file to be uploaded to vManage.
        required: true
        type: str
    fileName:
        description: name of file to be uploaded to vManage.
        required: true
        type: str
    debug:
        description: detailed debug on module lvl with using print statements
        required: false
        type: bool
author:
    - Matt Schulman
Example playbook setup:
- name: Upload software image to vManage
  viptela_software_upload:
    vmanage: "{{ ansible_host }}"
    cookie: "{{ login_result.set_cookie }}"
    token: "{{ token_result.content }}"
    fileName: "{{ srcPath }}/{{ fileName }}"
  register: upload_result

'''
import requests
import pprint
import urllib3
from ansible.module_utils.basic import AnsibleModule

# Class definitions
class ViptelaAPI(object):
  ''' Viptela API Operations'''

  # Public Methods
  def __init__(self, vmanage, cookie, token, srcPath, fileName, debug = False):
    self.vmanage = vmanage
    self.cookie = cookie
    self.token = token
    self.srcPath = srcPath
    self.fileName = fileName
    self.statusCode = ""

    self.fullPath = self.srcPath + '/' + self.fileName

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
  
  def softwareUpload(self):
    ''' Connect to vManage and upload a file '''

    self.print_debug(" -- upload: ", "", 1)
    self.print_debug(" -- vmanage: ", self.vmanage, 1)
    self.print_debug(" -- cookie: ", self.cookie, 1)
    self.print_debug(" -- token: ",self.token, 1)
    self.print_debug(" -- srcPath: ", self.srcPath,1)
    self.print_debug(" -- fileName: ", self.fileName, 1)
    self.print_debug(" -- fullPath: ", self.fullPath, 1)

    urllib3.disable_warnings()

    url = 'https://' + self.vmanage + '/dataservice/device/action/software/package'
    self.print_debug(" -- url: ", url, 1)

    payload = {
       'Content-Type': 'application/x-gzip',
       'validity': 'valid',
       'upload': 'true'
    }

    files = [
       ('file', (self.fileName, open(self.fullPath, 'rb'), 'application/octet-stream'))
    ]

    headers = {
       'X-XSRF-TOKEN': self.token,
       'Cookie': self.cookie
    }
  

    self.print_debug("  -- headers: ", headers, 1)

    response = requests.request('POST', url, headers=headers, data=payload, files=files, verify=False)

    self.print_debug("  -- status_code: ", response.status_code, 1)
    self.statusCode = str(response.status_code)
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
    "srcPath": { "type": 'str', "required": True },
    "fileName": { "type": 'str', "required": True },
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
    module.params['srcPath'],
    module.params['fileName'],
    module.params['debug']
  )

  viptelaSession.print_debug("-- viptela-softwareUpload: ", "", 1)
  if module.check_mode:
    module.exit_json(**viptelaSession.result)
  
   # do action + output structure enrichment and evaluation
  if viptelaSession.softwareUpload():
    viptelaSession.result["last_status"] = viptelaSession.statusCode
    viptelaSession.result['changed'] = True       
  else:
    viptelaSession.result["stdout_lines"] = viptelaSession.statusCode
    module.fail_json(msg='viptela Code Upload error.  Check last_status', **viptelaSession.result)

  # Return output structure
  module.exit_json(**viptelaSession.result)

if __name__ == "__main__":
  main()