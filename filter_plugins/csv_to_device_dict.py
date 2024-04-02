#/usr/bin/python
# Ansible custom filter plugin
# Description: Take an input CSV and convert to a dictionary
# Version: 1.0
# Author: Matt Schulman

'''
Read in a CSV and create a structure like:
[
  {
    "hostname": "<hostname>",
    "systemIP": "<systemIP>",
    "version": "<version>",
    "vpn": "<vpn>"
  },
  {
    "hostname": "<hostname>",
    "systemIP": "<systemIP>",
    "version": "<version>",
    "vpn": "<vpn>"
  }
  .
  .
  .
]
	
'''
import csv
class FilterModule(object):
  def filters(self):
    return {
      'csv_to_device_dict': self.csv_to_device_dict
    }
  
  @staticmethod
  def csv_to_device_dict(fileName):
    with open(fileName, 'r', encoding='utf-8-sig') as file:
      csv_reader = csv.DictReader(file)
      device_list = [row for row in csv_reader]
    
    # #Convert a single version string to a list
    # for device in device_list:
    #   version_list = []
    #   # if isinstance(device['versionsToDelete'], str):
    #   #   version_list.append(device['versionsToDelete'])
    #   if device['versionsToDelete']:
    #     version_list = device['versionsToDelete'].split(',')
    #     device['versionsToDelete'] = version_list
    
    return device_list