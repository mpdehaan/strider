
#!/usr/bin/python
# example strider file

from strider import Strider
from strider.virt.ec2 import EC2
from strider.provisioners.ansible_ssh import AnsibleSSH
import os

my_instance = EC2(
    name                   = "strider-test-3",
    region                 = "us-east-1",
    access_key_id          = os.environ["AWS_ACCESS_KEY"],
    secret_access_key      = os.environ["AWS_SECRET_KEY"],
    session_token          = os.environ.get("AWS_SESSION_TOKEN"),
    user_data              = None,
    image_id               = "ami-a7e145cc", # Ubuntu 14.04 us-east1 EBS
    instance_type          = "m3.medium",
    key_name               = os.environ["AWS_KEYPAIR"],
    security_groups        = [ os.environ["AWS_SECURITY_GROUP"] ],
    ssh = dict(
      public_ip        = True,
      username         = "ubuntu",
      private_key_path =  os.environ.get("AWS_PEM_FILE")
    )
)

# TODO: this is really just a shell provisioner, I plan to make this simpler and more generic.
# and AnsibleSSH should be able to inherit from it.

provisioner = AnsibleSSH(
    copy_from       = "./examples/ansible",
    copy_to         = "/home/ubuntu/deploy_root/",
    prep_cmds       = [
        # TODO: only do this if not recently updated
        "sudo apt-get update",
        # TODO: only do this if not installed
        "sudo apt-get install ansible",
    ],
    playbook_cmd    = "sudo ansible-playbook -i 'localhost,' -c local /home/ubuntu/deploy_root/ansible/test.yml"
)

instances = [ my_instance ]
strider = Strider(provisioner=provisioner)

# EITHER OF THESE ARE IMPLEMENTED!
strider.up(instances)
# strider.provision(instances)

# TODO:
#strider.list(instances)
#strider.destroy(instances)

#strider.cli()
