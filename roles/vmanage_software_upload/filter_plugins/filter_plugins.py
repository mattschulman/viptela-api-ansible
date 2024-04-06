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
      'validate_file_upload': self.validate_file_upload
    }
  
  def validate_file_upload(self, file, repo_list):
    repo_file_map = ""
    repo_file_map_list = []
    file_exists = False
    for repo_file in repo_list:
      repo_file_map_list = repo_file['fileNameMap'].replace('{','').replace('}','').split(',')
      # print(repo_file_map_list)
      for file_map in repo_file_map_list:
        repo_file_map = file_map.split('=')[1]
        # print(repo_file_map)
        if file == repo_file_map:
          # print('Found!')
          file_exists = True
          break

    # print(validated_fileDict_list)
    # print(skipped_fileDict_list)

    return file_exists
