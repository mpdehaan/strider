
#!/usr/bin/python
# example strider file

from strider import Strider
from strider.virt.ec2 import EC2
from strider.provisioners.shell import Shell
import os

# ====================================================
# cloud instance and builder configuration

my_instance = EC2(

    # the basics
    name                      = "%s-strider-test-3" % os.environ["USER"],
    region                    = "us-east-1",
    image_id                  = "ami-a7e145cc", # Ubuntu 14.04 us-east1 EBS
    instance_type             = "m3.medium",

    # only used if baking AMIs (--bake)
    bake_name                 = "strider-produced-ami",
    bake_description          = "AMI description goes here version 1.00",

    # security access info.  Can supply a security token if using one.  
    # TODO: SOON: make this grok BOTO profiles
    access_key_id             = os.environ["AWS_ACCESS_KEY_ID"],
    secret_access_key         = os.environ["AWS_SECRET_ACCESS_KEY"],
    # security_token          = os.environ.get("AWS_SESSION_TOKEN"),

    # which AWS key pair key to inject
    key_name                  = os.environ["AWS_KEYPAIR"],

    # various misc parameters:
    security_groups           = [ os.environ["AWS_SECURITY_GROUP"] ],
    # instance_profile_name   = "default",
    # subnet_id               = "foo",
    # user_data               = open("user-data.sh").read(),
    # block_device_map        = {
    #    '/dev/sdx' : dict(size=10),
    #    '/dev/sdy' : dict(snapshot_id='snap-12345678', size=10),
    # },

    # tags are also optional
    tags  = dict(
      role = "foo-test"
    ),

    # how to SSH into the instance
    # use the public IP or the private one, which user, what pem file path, etc
    ssh = dict(
      public_ip               = True,  
      username                = "ubuntu",
      private_key_path        =  os.environ.get("AWS_PEM_FILE")
    )

)

# ====================================================
# The provisioner decides how the instance will be
# configured and is not aware of the cloud provider

provisioner = Shell(

    # rsync controls
    copy_from  = "./examples/ansible",
    copy_to    = "/home/ubuntu/deploy_root/",

    # run these on commands on the instance
    commands   = [
        "sudo apt-get update",
        "sudo apt-get install ansible",
        "sudo ansible-playbook -i 'localhost,' -c local /home/ubuntu/deploy_root/ansible/test.yml -v 2>&1"
    ]

)

# ====================================================
# go!

instances = [ my_instance ]
strider = Strider(provisioner=provisioner)
strider.cli(instances)

