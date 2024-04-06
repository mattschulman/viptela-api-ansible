#!/usr/bin/python
# Ansible custom filter plugin
# Description: filters which will handle actions to remove the last number from a cedge version
# Version: 0.1
# Author: Matt Schulman

class FilterModule(object):
  def filters(self):
    return {
      'normalize_version': self.normalize_version,
      'generate_install_payload': self.generate_install_payload
    }
  
  def normalize_version(self, version):
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
  
  def generate_install_payload(self, dummy, versionToInstall, device_list, reboot):
    payloadDict = {
      'action': 'install',
      'input': {
        'vEdgeVPN': 0,
        'vSmartVPN': 0,
        'version': versionToInstall,
        'versionType': 'vmanage',
        'reboot': reboot,
        'sync': True
      },
      'devices': [],
      'deviceType': 'vedge'
    }

    # Generate the devices key as a list of device IPs and deviceIDs if the inputted version matches the version for this API call
    for device in device_list:
      if device['version'] == versionToInstall:
        installDeviceDict = {
          'deviceIP': device['systemIP'],
          'deviceId': device['deviceID']
        }
        payloadDict['devices'].append(installDeviceDict)
    
    return payloadDict
    
      