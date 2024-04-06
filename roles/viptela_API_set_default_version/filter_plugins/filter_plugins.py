#!/usr/bin/python
# Ansible custom filter plugin
# Description: filters which will handle actions to remove the last number from a cedge version, 
# validate that the version is in the correct spot in the vedge info from vmanage to generate a valid list
# and also to generate a skipped list for versions that are not in the correct spot in the vedge info from vmanage
# Version: 0.1
# Author: Matt Schulman

class FilterModule(object):
  def filters(self):
    return {
      'normalize_version': self.normalize_version,
      'validate_setDefault_versions': self.validate_setDefault_versions,
      'create_setDefault_skipped_versions': self.create_setDefault_skipped_versions
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
    
  def validate_setDefault_versions(self, device_list, vmanage_software_list):
    # Go through each device in self.device_list, and validate that the version is in the list of availableVersions
    new_device_list = []
    skipped_device_list = []
    for device in device_list:
      device['version'] = self.normalize_version(device['version'])
      for dev in vmanage_software_list:
      # Find the record that contains the device['systemIP']
        if 'system-ip' in dev:
          if device['systemIP'] == dev['system-ip']:
            if (device['version'] in dev['availableVersions'] or dev['version'] == device['version']) and  dev['defaultVersion'] != device['version']:
              new_device_list.append(device)
            else:
              skipped_device_list.append(device)
    return new_device_list
  
  def create_setDefault_skipped_versions(self, device_list, vmanage_software_list):
    # Go through each device in self.device_list, and validate that the version is in the list of availableVersions
    new_device_list = []
    skipped_device_list = []
    for device in device_list:
      device['version'] = self.normalize_version(device['version'])
      for dev in vmanage_software_list:
      # Find the record that contains the device['systemIP']
        if 'system-ip' in dev:
          if device['systemIP'] == dev['system-ip']:
            if (device['version'] in dev['availableVersions'] or dev['version'] == device['version']) and  dev['defaultVersion'] != device['version']:
              new_device_list.append(device)
            else:
              skipped_device_list.append(device)
    return skipped_device_list
  
  def generate_setDefault_payload(self, device_list):
    # Create the payload structure.  The devices list will be appended in a for loop.
    payloadDict =  {
      'action': 'defaultpartition',
      'devices': [],
      'deviceType': 'vedge'
    }

    # Generate the devices key as a list of device IPs and device IDs
    for device in device_list:
      setDefaultDeviceDict = {
        'version': self.normalize_version(device['version']),
        'deviceIP': device['systemIP'],
        'deviceId': device['deviceID']
      }
      payloadDict['devices'].append(setDefaultDeviceDict)

    return payloadDict
    
      