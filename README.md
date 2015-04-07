# ansible-cloudformation-example
working example(s) of creating cloudformation stacks in yaml and uploading via ansible

# how to run
Obviously, YMMV, some things are hardcoded.

    AWS_PROFILE="" ansible-playbook -c local -i "localhost," test1-single-ec2.yml
    AWS_PROFILE="" ansible-playbook -c local -i "localhost," test2-full-vpc.yml -e "stack_name=test2a stack_cidr=10.4"
    AWS_PROFILE="" ansible-playbook -c local -i "localhost," test2-full-vpc.yml -e "stack_name=test2b stack_cidr=10.5"

# tips

* Spend a lot of time on the cloudformation console to look for errors. Some will kill the 'reason' column.
* If there's a major problem with autoscaling, it only shows up in the EC2->autoscaling panel.


# library patches
Since Ansible always has a huge backlog of pull requests, it's necessary to have a local copy of new or patched modules. The modules in `library/` are from the following repos or pull requests:

* `cloudformation_assemble`: https://github.com/ansible/ansible-modules-core/pull/1034
