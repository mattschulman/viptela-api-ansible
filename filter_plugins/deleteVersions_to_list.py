#/usr/bin/python
# Ansible custom filter plugin
# Description: Convert a version string to a list
# Version: 1.0
# Author: Matt Schulman
class FilterModule(object):
  def filters(self):
    return {
      'deleteVersions_to_list': self.deleteVersions_to_list
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
