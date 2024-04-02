#/usr/bin/python
# Ansible custom filter plugin
# Description: Take the vedge info output from vManage API call, extract the device IP and UUID and add to device dictionary list
# Version: 1.0
# Author: Matt Schulman

class FilterModule(object):
  def filters(self):
    return {
      'parse_device_info': self.parse_device_info
    }
  
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