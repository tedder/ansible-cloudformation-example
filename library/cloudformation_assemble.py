#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import yaml
import json

DOCUMENTATION = '''
---
module: cloudformation_assemble
short_description: assemble an AWS Cloudformation JSON template from a collection of YML files
description:
     - Convert YML to JSON.
     - Combine many files so a single template can be sanely organized
version_added: "2.0"
options:
  directory:
    description:
      - base directory for this cloudformation stack configuration
    default: "cfbuild"
  destination:
    description:
      - file where compiled template JSON will be placed
    default: "/tmp/cfbuild.json"
  subdirs:
    description:
      - if absent, all subdirectories will be compiled
      - if present, comma-delimited list of subdirectories that will be compiled

notes:
  - The file structure for cloudformation_assemble expects subdirectories to be created. Inside those are up to five yml files, corresponding to the five sections of a Cloudformation template. Here's a sample layout:
    cfbuild/meta.yml
    cfbuild/web/resources.yml
    cfbuild/web/mappings.yml
    cfbuild/web/outputs.yml
    cfbuild/web/conditions.yml
    cfbuild/web/parameters.yml
    cfbuild/web/resources.yml

requirements: [ "boto" ]
author: Ted Timmons, Andrew Cholakian
extends_documentation_fragment: aws
'''

EXAMPLES = '''
# Assuming the following files are in place:
mkdir -p files/cf-example/basic-server/
cat <<"EOF" > files/cf-example/basic-server/resources.yml
server:
  Type: AWS::EC2::Instance
  Properties:
    KeyName: "my-ssh-key"
    ImageId: ami-d85e75b0
    InstanceType: t1.micro
    AvailabilityZone: "us-east-1a"
EOF

cat <<"EOF" > files/cf-example/meta.yml
AWSTemplateFormatVersion: '2010-09-09'
Description: Sample Stack
EOF

## simple example


- name: assemble subset of a cloudformation stack
  local_action: cloudformation_assemble directory=files/cf-example subdirs=basic-server
  run_once: true
- name: Launch cloudformation using compiled json
  local_action: cloudformation stack_name="test1" state=present region=us-east-1 disable_rollback=yes template=/tmp/cfbuild.json
  run_once: true

## more typical example, uses files in http://github.com/stansonhealth

- name: assemble entire cloudformation stack
  local_action: cloudformation_assemble directory=files/cf-typical
  run_once: true
- name: Launch cloudformation using compiled json
  local_action: cloudformation stack_name="test2" state=present region=us-east-1 disable_rollback=yes template=/tmp/cfbuild.json
  run_once: true
  args:
    template_parameters:
      KeyName: "{{aws_east_key_name}}"
'''

def read_yaml(filepath):
    f = open(filepath, 'r')
    if not f:
        module.fail_json(msg="Could not find file: " + f)

    try:
        return yaml.load(f) or dict()
    except yaml.YAMLError, ex:
        module.fail_json("Could not parse YAML: %s" % ex)

def main():
    module = AnsibleModule(
        argument_spec = dict(
            directory=dict(default="cfbuild"),
            destination=dict(default="/tmp/cfbuild.json"),
            subdirs=dict(default='')
        )
    )

    params = module.params
    directory = params['directory']
    subdirs = params['subdirs']
    destination = params['destination']
    
    monolith = dict(
        Parameters=dict(),
        Mappings=dict(),
        Resources=dict(),
        Outputs=dict(),
        Conditions=dict()
    )

    meta = os.path.join(directory, 'meta.yml')
    monolith.update(read_yaml(meta))

    fns_properties = dict()
    fns_properties["parameters.yml"] = "Parameters"
    fns_properties["mappings.yml"]   = "Mappings"
    fns_properties["resources.yml"]  = "Resources"
    fns_properties["outputs.yml"]    = "Outputs"
    fns_properties["conditions.yml"] = "Conditions"
    debug = []

    for subdir in subdirs.split(','):
      currdir = os.path.join(directory, subdir)
      for root, _, files in os.walk(currdir):
        for f in files:
             debug.append("file: %s" % f)
             fullpath = os.path.join(root, f)
             debug.append("fullpath: %s" % fullpath)
             debug.append("basename: %s" % os.path.basename(fullpath))
             debug.append("basename+dirname: %s" % os.path.basename(os.path.dirname(fullpath)))
             debug.append("split: %s" % str(os.path.split(fullpath)))
             if f in fns_properties:
                 key = fns_properties[f]
                 if key:
                     monolith[key].update(read_yaml(fullpath))

                     
    dest_f = open(destination, "w")
    json.dump(monolith, dest_f, indent=2)
    
    changed = True # we aren't idempotent, yet.
    module.exit_json(directory=directory, destination=destination, debug="<br />\n".join((debug)), changed=changed)

# Import module snippets
from ansible.module_utils.basic import *
main()
