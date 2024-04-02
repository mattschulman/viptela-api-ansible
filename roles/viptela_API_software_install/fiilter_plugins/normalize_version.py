#!/usr/bin/python
# Ansible custom filter plugin
# Description: filters which will handle actions to remove the last number from a cedge version
# Version: 0.1
# Author: Matt Schulman

class FilterModule(object):
  def filters(self):
    return {
      'normalize_version': self.normalize_version
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
    
      