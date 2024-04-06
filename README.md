# viptela-api-ansible
API Calls for Cisco SDWAN via Ansible

# Ansible Playbooks
## vmanage_upload_main.yml
This playbook will import a CSV file called "vmanage_upload_input.csv" into a list of dictionaries (custom filter).  It will authenticate to vManage (defined in inventory) to get the cookie and XSRF token.  It will perform an API call to get the software repo information.  Using that information, it will validate that the files in the input CSV are not already uploaded to vmManage (custom filter).  If a file is, the dictionary for it will be added to a skipped list.  If there are items in the validated file list, it will call the "vmanage_software_upload" role.  Finally it will display the list of skipped files if there is one.

### vmanage_software_upload role
This role will perform an API call to vmanage to upload the software file.  After it completes, it will gather the software repo info  from vManage and validate that the file is in the repo (custom filter). 

### Format of vmanage_upload_input.csv
Should have 2 columns, one for the File Path, and one for the File Name.
srcPath,fileName

## code_upgrade_main.yml
This playbook will import a CSV file called "upgrade_device_input.csv" into a list of dictionaries (custom filter).  It will also read in a file called "upgrade.input.json" (into a dictionary called inputDict) which will define which actions to take (using booleans).  There are three actions to that can be enabled: "install-image", "activate-version", and "set-default-version".  

It will authenticate to vManage (defined in inventory) to get the cookie and XSRF token.   It will get the valid device info via API from vManage and use it to lookup the system IP and UUID for each device in the input CSV file and populate the fields in the device dictionary. 

If "install-image" is true in the inputDict, then it will create a unique list of software versions from the device dictionary.  This is because the install API can only run on a single version.  It will loop through the unique version list and call the "viptela_API_software_install" role passing in the version as "versionToInstall" variable.

If "install-image" is false and "activate-version" is true (if both are true, it is handled by the viptela_API_software_install role),  the "viptela_API_activate_version" role is called.

If "set-default-version" is set to true, the "viptela_API_set_default_version" role is called.

### viptela_API_software_install role
This role will get the software repo info from vManage and validate that the versionToInstall is in the repo.  If it is, it will build the POST message body (custom filter) and then make the API call to vManage (if "activate-version" action was set to true, this will request that vManage activate the version as well and the device will reboot into the new version).  vManage will return a job ID in the reponse.  The playbook will then continue to get the job status via API call every minute  until it sees that the job is completed.    Once it is completed, it will get the device info from vManage via API call and then validate that for each device the versionToInstall shows up in the "availableVersions" (if not activated) list or is equal to the "version" key (if activated) in the device info by importing the tasks from "validate_software_install.yml".

### viptela_API_activate_version role
This role will get the device info from vManage and for each device it will validate that the version is in the "availableVersions" list to create a validated device list (custom filter).  If it is not, will add the device dictionary into a skipped list (custom filter).

If there are entries in the validated device list, it will generate the API POST body (custom filter) and send the API POST to vManage.  vManage will return a job ID in the reponse.  The playbook will then continue to get the job status via API call every minute  until it sees that the job is completed.    Once it is completed, it will get the device info from vManage via API call and then validate that for each device the version is equal to the "version" key for that device in the device info by importing the tasks from "validate_software_activate.yml"

If there are entries in the skipped list, it will display them.

### viptela_API_set_default_version role
This role will get the device info from vManage and for each device it will validate that the version is in the "availableVersions" list or the "version" key to create a validated device list (custom filter).  If it is not, will add the device dictionary into a skipped list (custom filter).

If there are entries in the validated device list, it will generate the API POST body (custom filter) and send the API POST to vManage.  vManage will return a job ID in the reponse.  The playbook will then continue to get the job status via API call every minute  until it sees that the job is completed.    Once it is completed, it will get the device info from vManage via API call and then validate that for each device the version is equal to the "defaultVersion" key for that device in the device info by importing the tasks from "validate_set-default.yml"

If there are entries in the skipped list, it will display them.

### Format of upgrade_device_input.csv
Four columns:
hostname,systemIP,deviceID,version

If systemIP or deviceID are not present, they will be looked up via API call.

### Format of upgrade_input.json
{
  "Actions": {
    "install-image": false,
    "activate-version": true,
    "set-default-version": true
  }
}

Set the action that you wish to happen to be true, otherwise set it to false.

Having activate-verion set to true, without install-image set to true assumes that the software image was already installed.

Haveing set-default-version set to true assumes that the version is already installed and/or activated on the device.

## delete_version_main.yml
This playbook reads in a CSV file called "delete_version_device_input.csv" and converts to a dictionary (custom filter).  

It will authenticate to vManage (defined in inventory) to get the cookie and XSRF token.   It will get the valid device info via API from vManage and use it to lookup the system IP and UUID for each device in the input CSV file and populate the fields in the device dictionary. 

It then calls the viptela_API_delete_version role.

### viptela_API_delete_version role
This role will get the device info from vManage.

If no versions were defined, it will gather the "availableVersions" list for the the device from vManage and use that as the versions to delete list. (intent is to delete all inactive, non-default versions on the device.)

For each version in the versions to delete list, it will validate that that the version is in the "availableVersions" list and will add the version and device info to a validated version list (custom filter).  If the version matches the "version" key or the "defaultVersion" key, or is not in the "availableVersions" list, it will add that version and the device info to a skipped version list (custom filter).

If there are entries in the validated versions list, it will generate the body for the API post (custom filter) and then send the API call to vManage.  vManage will return a job ID in the reponse.  The playbook will then continue to get the job status via API call every minute  until it sees that the job is completed.    Once it is completed, it will get the device info from vManage via API call and then validate that for each device each version is not in the "availableVersions" key for that device by importing the tasks from "validate_software_removal.yml"

### delete_version_device_input.csv
Four columns:
hostname,systemIP,deviceID,versionsToDelete

If systemIP or deviceID are not present, they will be looked up via API call.

Verions in the versionsToDelete column should be enclosed in double-quotes.
If a single version is to be deleted, just put the version in quotes
ie:
"20.6.6" or "17.06.05a.0.6"

If multiple versions are to be deleted, separate them with commas (enclosing in double-quotes)
ie:
"20.3.8,20.6.6" or "17.06.05a.0.6,17.03.08a.0.6"

If you want to delete all inactive, non-default versions (you cannot delete the active version or the default version), leave the versionsToDelete column blank.

## vmanage_authenticate.yml
This playbook simply authenticates to vmanage and then gets the session cookie and XSRF token and prints them to the screen.