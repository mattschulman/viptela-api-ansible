#!/usr/bin/python
# Ansible custom filter plugin
# Description: filters for delete_version role
# Version: 0.1
# Author: Matt Schulman

class FilterModule(object):
  def filters(self):
    return {

      'normalize_version': self.normalize_version,
      'validate_delete_versions': self.validate_delete_versions,
      'generate_delete_version_payload': self.generate_delete_version_payload
    }
  
  def deleteVersions_to_list(self,device_list):
    for device in device_list:
      version_list = []
      # if isinstance(device['versionsToDelete'], str):
      #   version_list.append(device['versionsToDelete'])
      if device['versionsToDelete']:
        version_list = device['versionsToDelete'].split(',')
        device['versionsToDelete'] = version_list
    return device_list

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
  
  def validate_delete_versions(self, device_list, vmanage_software_list):
    # Go through each device in self.device_list, and validate that the version is in the list of availableVersions
    # And not the default_version
    new_device_list = []
    for device in device_list:
      version_list = []
      new_version_list = []
      skipped_version_list = []
      version_list = device['versionsToDelete']
      for dev in vmanage_software_list:
        # Find the record that contains the device['systemIP']
        if device['systemIP'] == dev['system-ip']:
          # print(dev['system-ip'])
          # If device['versionsToDelete'] is empty, set the version_list to the availableVersions for the device.
          if not device['versionsToDelete']:
            # print("empty list inputted")
            version_list = dev['availableVersions']
          # For each version, validate that it is in the available versions list and not the default version.
          # If it is, append it to new_version_list.
          for version in version_list:
            # print(version)
            # print(dev['availableVersions'], dev['defaultVersion'])
            if version in dev['availableVersions'] and version != dev['defaultVersion']:
              # print(dev['availableVersions'], dev['defaultVersion'])
              # print("Match!")
              new_version_list.append(version)
            else:
              # print("Skipped!")
              skipped_version_list.append(version)
      
      #Append the new device list, hostname, systemIP, deviceID, new_version_list, and skipped_version_list to the new_device_list as dictionary.  
      new_device_list.append({'hostname': device['hostname'],'systemIP': device['systemIP'], 'deviceID': device['deviceID'], 'versionsToDelete': new_version_list, 'skippedVersions': skipped_version_list})
      
    return new_device_list
  
  def generate_delete_version_payload(self, device_list):
    # Create the payload structure as a dictionary.  Then add the devices list from a loop.
    payloadDict = {
      'action': 'removepartition',
      'devices': [],
      'deviceType': 'vedge'
    }
  
    for device in device_list:
      deleteDeviceDict = {
        'version': device['versionsToDelete'],
        'deviceIP': device['systemIP'],
        'deviceId': device['deviceID']
      }
      payloadDict['devices'].append(deleteDeviceDict)

    return payloadDict
   