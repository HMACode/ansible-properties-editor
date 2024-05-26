#!/usr/bin/python

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule
import os, datetime, shutil



DOCUMENTATION = r'''
---
module: properties_editor
short_description: edit properties file
version_added: "1.0.0"
description: edit properties file, update existing entries, delete entries or create new ones

options:
    filepath:
        description: Path to properties file
        required: true
        type: str
    backup:
        description: Backup or not the existing properties file
        required: false
        type: bool
    properties:
        description: list of properties that needs to be updated or deleted
        required: true
        type: list

author:
    - HMACode
'''

EXAMPLES = r'''
- name: Sample module call
    properties_editor:
    filepath: "/data/test.properties"
    properties:
        - key: "user.name"
          value: "jeff"
          action: update
        - key: "user.password"
          action: "delete"
        - key: "user.age"
          value: "59"
          action: update
'''

def update_properties(file_path, updates, keys_to_delete):
    now = str(datetime.datetime.now())
    changed = False
    with open(file_path, 'r') as file:
        lines = file.readlines()
        updated_lines = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                split = line.split('=', 1)
                key = split[0].strip()
                current_value = split[1]

                if key in updates:
                    new_value = updates[key].strip()
                    if current_value != new_value:
                        changed = True
                        updated_lines.append(f"{key}={new_value}\n")
                    else:
                        updated_lines.append(line + '\n')
                    del updates[key]
                elif key in keys_to_delete:
                    changed = True
                    updated_lines.append("\n# The following property (%s) was removed by ansible on %s\n"%(key, now))
                    updated_lines.append('#' + line + '\n\n') 
                else:
                    updated_lines.append(line + '\n')
            else:
                updated_lines.append(line + '\n')
    
    with open(file_path, 'w') as file:
        file.writelines(updated_lines)

        # fill new properties
        # but first add a hint comment
        if updates:
            file.write("\n\n# Added by ansible at %s\n"%(now))
            changed = True
            for key, value in updates.items():
                file.write(f"{key}={value}\n")
            file.write("#################\n")
    return changed

def run_module():
    
    module_args = dict(
        filepath=dict(type='str', required=True),
        backup = dict(type='bool', required=False, default=True),
        properties=dict(type='list',elements='dict',
            options=dict(
                key=dict(type='str', required=True),
                value=dict(type='str', required=False),
                action=dict(type='str', required=True)
            ), required=True)
    )


    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    result = dict(
        changed=False
    )


    if module.check_mode:
        module.exit_json(**result)

    # Check module arguments are correct
    # Check file exists
    properties_file_path = module.params['filepath']
    if not os.path.exists(properties_file_path):
        module.fail_json("file '%s' does not exist"%(properties_file_path))

    # Check each property
    for prop in module.params['properties']:
        supported_actions = ['update', 'delete']
        action = prop['action']
        if action not in supported_actions:
            module.fail_json(msg="Unsupported action: '%s'"%(action))
        
        if action == 'update' and prop['value'] is None:
            module.fail_json(msg="Please specify the value you want to set for the key: '%s'"%(prop['key']))
        
        key = prop['key']
        if ' ' in key:
            module.fail_json(msg="Invalid key: '%s'. keys should not contains spaces"%(prop['key']))


    # Backup if necessary
    if module.params['backup']:
        bkup_file_path = properties_file_path + '.ansbile-bkup_' + datetime.datetime.now().strftime('%d-%m-%Y_%H:%M')
        shutil.copy(properties_file_path, bkup_file_path)

    

    updates = {}
    keys_to_delete = []
    for param in module.params['properties']:
        if param['action'] == 'update':
            updates[param['key']] = param['value']
        elif param['action'] == 'delete':
            keys_to_delete.append(param['key'])

    # update now ... 
    result['changed'] = update_properties(properties_file_path, updates, keys_to_delete)

    module.exit_json(**result)


def main():
    run_module()

if __name__ == '__main__':
    main()