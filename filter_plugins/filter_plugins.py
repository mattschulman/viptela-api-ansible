#!/usr/bin/python
# Ansible custom filter plugin
# Description: filters which will handle actions to remove the last number from a cedge version, 
# validate that the version is in the correct spot in the vedge info from vmanage to generate a valid list
# and also to generate a skipped list for versions that are not in the correct spot in the vedge info from vmanage
# Version: 0.1
# Author: Matt Schulman

import csv

class FilterModule(object):
  def filters(self):
    return {
      'csv_to_device_dict_multi_vmanage': self.csv_to_device_dict_multi_vmanage,
      'csv_to_device_dict': self.csv_to_device_dict,
      'deleteVersions_to_list': self.deleteVersions_to_list,
      'normalize_version': self.normalize_version,
      'validate_files': self.validate_files,
      'parse_device_info': self.parse_device_info,
      'generate_skipped_file_list': self.generate_skipped_file_list
    }
  
  @staticmethod
  def csv_to_device_dict_multi_vmanage(dummy, fileName):
    with open(fileName, 'r', encoding='utf-8-sig') as file:
      csv_reader = csv.DictReader(file)
      device_list = [row for row in csv_reader]
    
    data_dict_list = []
    temp_dict={}

    #Create the initial data_dict list structure of one dictionary per vManage IP
    for device in device_list:
      if device['vmanageIP'] not in temp_dict.values():
        temp_dict['vmanageIP'] = device['vmanageIP']
        data_dict_list.append(temp_dict.copy())
    
    # Create the next device_data key which is a list for each vmanage IP
    for item in data_dict_list:
      # If the device_data key is not in the item dictionary, create it as an empty list
      if 'device_data' not in item.keys():
        item.update({'device_data': []})

      for device in device_list:

        # Get the rest of the fields in the row in a temp dictionary
        temp_device_list = {'hostname':device['hostname'], 'systemIP': device['systemIP'],'version': device['version'], 'vpn': device['vpn']}

        # If the vmanageIP matches the current key, append the device info dictionary into it
        if item['vmanageIP'] == device['vmanageIP']:
          item['device_data'].append(temp_device_list)
    
    return data_dict_list


  @staticmethod
  def validate_files(fileDict_list, repo_list):
    validated_fileDict_list = []
    skipped_fileDict_list = []
    repo_file_map = ""
    repo_file_map_list = []
    for fileDict in fileDict_list:
      file_exists = False
      for repo_file in repo_list:
        repo_file_map_list = repo_file['fileNameMap'].replace('{','').replace('}','').split(',')
        # print(repo_file_map_list)
        for file_map in repo_file_map_list:
          repo_file_map = file_map.split('=')[1]
          # print(repo_file_map)
          if fileDict['fileName'] == repo_file_map:
            # print('Found!')
            file_exists = True
            skipped_fileDict_list.append(fileDict)
            break
      if not file_exists:
        validated_fileDict_list.append(fileDict)

    # print(validated_fileDict_list)
    # print(skipped_fileDict_list)

    return validated_fileDict_list

  @staticmethod
  def csv_to_device_dict(fileName):
    with open(fileName, 'r', encoding='utf-8-sig') as file:
      csv_reader = csv.DictReader(file)
      device_list = [row for row in csv_reader]
    
    return device_list

  @staticmethod
  def deleteVersions_to_list(device_list):
    for device in device_list:
      version_list = []
      # if isinstance(device['versionsToDelete'], str):
      #   version_list.append(device['versionsToDelete'])
      if device['versionsToDelete']:
        version_list = device['versionsToDelete'].split(',')
        device['versionsToDelete'] = version_list
    return device_list
  
  @staticmethod
  def normalize_version(version):
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
    
  @staticmethod
  def parse_device_info(input_device_list, api_device_list):
    #Loop through the inputted device list and then loop through the device info list from API
    for upgrade_device in input_device_list:  
      for device in api_device_list['json']['data']:
        #As long as there's a host-name key in the device info list from API, check for a match of hostnames to find the right device
        if 'host-name' in device.keys():
          if upgrade_device['hostname'] == device['host-name']:
            # print(f'SystemIP: {upgrade_device['systemIP']} UUID: {device['uuid']}')
            # If the system IP is missing from the input list, set it to the system IP from the device info from API
            if upgrade_device['systemIP'] == "":
              upgrade_device['systemIP'] = device['system-ip']
            # if the system ID is missing from the input list, set it to the UUID from the device info.
            if upgrade_device['deviceID'] == "":
              upgrade_device['deviceID'] = device['uuid']
            
    return input_device_list

  @staticmethod
  def generate_skipped_file_list(fileDict_list, repo_list):
    validated_fileDict_list = []
    skipped_fileDict_list = []
    repo_file_map = ""
    repo_file_map_list = []
    for fileDict in fileDict_list:
      file_exists = False
      for repo_file in repo_list:
        repo_file_map_list = repo_file['fileNameMap'].replace('{','').replace('}','').split(',')
        # print(repo_file_map_list)
        for file_map in repo_file_map_list:
          repo_file_map = file_map.split('=')[1]
          # print(repo_file_map)
          if fileDict['fileName'] == repo_file_map:
            # print('Found!')
            file_exists = True
            skipped_fileDict_list.append(fileDict)
            break
      if not file_exists:
        validated_fileDict_list.append(fileDict)

    # print(validated_fileDict_list)
    # print(skipped_fileDict_list)

    return skipped_fileDict_list