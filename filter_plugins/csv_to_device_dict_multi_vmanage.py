#/usr/bin/python
# Ansible custom filter plugin
# Description: Take an input CSV and convert to a dictionary
# Version: 1.0
# Author: Matt Schulman

'''
Read in a CSV and create a structure like:
[
	{
		"vmanage": "<IP>",
		"device_data":
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
		]
	},
	{
		"vmanage": "<IP>",
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
		]
	},
  .
  .
  .
]
'''
import csv
class FilterModule(object):
  def filters(self):
    return {
      'csv_to_device_dict_multi_vmanage': self.csv_to_device_dict_multi_vmanage
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