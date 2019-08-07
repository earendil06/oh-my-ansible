#!/usr/bin/python

# Copyright: (c) 2019, Florent Pastor <flopastor06@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: file_properties

short_description: This module is used to manage .properties files mostly used in Java configuration projects

version_added: "2.4"

description:
    - "This module is used to manage .properties files mostly used in Java configuration projects"

options:
    output:
        description:
            - This is the output generated file .properties
        required: true
    input:
        description:
            - This is a file you can start with, and manipulate it as a set of initial properties
        required: false
    key_val:
        description:
            - The key-val pairs to add or modify
        required: false
    comment:
        description:
            - The keys to comment
        required: false
    uncomment:
        description:
            - The keys to uncomment
        required: false
    remove:
        description:
            - The keys to remove
        required: false    

author:
    - Florent Pastor (flopastor06@gmail.com)
'''

EXAMPLES = '''
# Pass in a message
- name: run the new module
  file_properties:
    output: "result.properties"
    key_val:
      key1: val1
      key2: val2
      key3: val3
    comment:
      - key2
- name: run the new module 2
  file_properties:
    input: "myFile.properties"
    output: "result.properties"
    comment:
      - key2
    uncomment:
      - key1
    remove:
      - key3
    key_val:
      another.key: anotherValue
'''

RETURN = '''
'''

from ansible.module_utils.basic import AnsibleModule


class Property:
    def __init__(self):
        self.comment = False
        self.key = ''
        self.value = ''


def init_properties(filename):
    f = open(filename, 'r')
    result = []
    for line in f.readlines():
        prop = Property()
        prop.comment = line.startswith('#')
        starting_index = 1 if prop.comment else 0
        [prop.key, prop.value] = line[starting_index:].split('=')
        result.append(prop)
    return result


def find_by_key(properties, key):
    for p in properties:
        if p.key == key:
            return p
    return None


module_args = dict(
    output=dict(type='str', required=True),
    input=dict(type='str', required=False, default=''),
    key_val=dict(type='dict', required=False, default=dict()),
    comment=dict(type='list', required=False, default=list()),
    uncomment=dict(type='list', required=False, default=list()),
    remove=dict(type='list', required=False, default=list())
)


def run_module():
    result = dict(
        changed=False,
        original_message='',
        message=''
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if module.check_mode:
        module.exit_json(**result)

    output_file = module.params['output']
    input_file = module.params['input']
    key_val = module.params['key_val']
    comments = module.params['comment']
    un_comments = module.params['uncomment']
    removes = module.params['remove']

    from_scratch = len(input_file) == 0

    if from_scratch and len(key_val) == 0:
        module.fail_json(msg='From scratch requires some values', **result)

    if from_scratch and len(output_file) == 0:
        module.fail_json(msg='The file name is incorrect', **result)

    properties = []
    if not from_scratch:
        try:
            properties = init_properties(input_file)
        except IOError:
            module.fail_json(msg='Error while trying to open the file', **result)

    for key, val in key_val.items():
        prop = find_by_key(properties, key)
        if prop is None:
            p = Property()
            p.key = key
            p.value = val
            properties.append(p)
        else:
            prop.value = val

    for key in comments:
        prop = find_by_key(properties, key)
        if prop is not None:
            prop.comment = True

    for key in un_comments:
        prop = find_by_key(properties, key)
        if prop is not None:
            prop.comment = False

    for key in removes:
        prop = find_by_key(properties, key)
        if prop is not None:
            properties.remove(prop)

    f = open(output_file, 'w')
    for prop in properties:
        f.write('{}{}={}\n'.format('#' if prop.comment else '', prop.key, prop.value))
    f.close()
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
