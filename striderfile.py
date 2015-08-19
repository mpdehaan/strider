
#!/usr/bin/python
# example strider file

from strider import Strider
from strider.virt.ec2 import EC2
from strider.provisioners.shell import Shell
import os

my_instance = EC2(
    name                      = "%s-strider-test-3" % os.environ["USER"],
    region                    = "us-east-1",
    access_key_id             = os.environ["AWS_ACCESS_KEY_ID"],
    secret_access_key         = os.environ["AWS_SECRET_ACCESS_KEY"],
    # instance_profile_name   = "default",
    # security_token          = os.environ.get("AWS_SESSION_TOKEN"),
    user_data                 = None,
    image_id                  = "ami-a7e145cc", # Ubuntu 14.04 us-east1 EBS
    instance_type             = "m3.medium",
    key_name                  = os.environ["AWS_KEYPAIR"],
    # subnet_id               = "foo",
    # user_data               = open("user-data.sh").read(),
    # block_device_map        = {
    #    '/dev/sdx' : dict(size=10),
    #    '/dev/sdy' : dict(snapshot_id='snap-12345678', size=10),
    # },
    tags  = dict(
      role = "foo-test"
    ),
    security_groups           = [ os.environ["AWS_SECURITY_GROUP"] ],
    ssh = dict(
      public_ip               = True,
      username                = "ubuntu",
      private_key_path        =  os.environ.get("AWS_PEM_FILE")
    )
)

provisioner = Shell(
    copy_from  = "./examples/ansible",
    copy_to    = "/home/ubuntu/deploy_root/",
    commands   = [
        "sudo apt-get update",
        "sudo apt-get install ansible",
        "sudo ansible-playbook -i 'localhost,' -c local /home/ubuntu/deploy_root/ansible/test.yml -v 2>&1"
    ]
)

instances = [ my_instance ]
strider = Strider(provisioner=provisioner)
strider.cli(instances)

