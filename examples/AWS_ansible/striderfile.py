
#!/usr/bin/python
# example strider file

from strider import Strider
from strider.virt.ec2 import EC2
from strider.provisioners.shell import Shell
import time
import os

# ==============================================================================
# cloud instance and builder configuration

instance = EC2(
    name                      = "%s-strider-test-3" % os.environ["USER"],
    region                    = "us-east-1",
    image_id                  = "ami-a7e145cc", # Ubuntu 14.04 us-east1 EBS
    instance_type             = "m3.medium",
    security_groups           = [ os.environ["AWS_SECURITY_GROUP"] ],
    key_name                  = os.environ["AWS_KEYPAIR"],
    ssh = dict(
        public_ip             = True,
        username              = "ubuntu",
        private_key_path      =  os.environ.get("AWS_PEM_FILE")
    ),
    tags  = dict(
        role                  = "foo-test"
    ),
    bake_name                 = "strider-produced-ami-%d" % int(time.time()),
    bake_description          = "AMI description goes here version 1.00",
    profile_name              = "dev", # from ~/.aws/credentials

    # alternative access credentials:
    # access_key_id           = os.environ["AWS_ACCESS_KEY_ID"],
    # secret_access_key       = os.environ["AWS_SECRET_ACCESS_KEY"],
    # security_token          = os.environ.get("AWS_SESSION_TOKEN"),

    # other optional parameters:
    user_data                 = open("userdata.sh").read(),
    # instance_profile_name   = "default", # (IAM)
    # subnet_id               = "foo",
    # block_device_map        = {
    #    '/dev/sdx' : dict(size=10),
    #    '/dev/sdy' : dict(snapshot_id='snap-12345678', size=10),
    # },
)

# ==============================================================================
# The provisioner decides how the instance will be configured

provisioner = Shell(
    commands = [

        # to select rsync, change 'copy' to 'rsync' below
	# rsync on AWS free tier has been observed to be unreliable - protocol errors
	# so if you see this, know why

	dict(type='rsync', copy_from="./deploy", copy_to="/home/ubuntu/deploy_root"),

        "sudo DEBIAN_FRONTEND=noninteractive apt-get update -y",
        "sudo DEBIAN_FRONTEND=noninteractive apt-get -y install ansible",
        "sudo PYTHONUNBUFFERED=1 ansible-playbook -i 'localhost,' -c local /home/ubuntu/deploy_root/deploy/test.yml -v 2>&1"
    ]
)

# optional steps to run prior to --bake commands that will only run with --bake
pre_bake = Shell(
    commands = [
        "sync"
    ]
)

# optional commands to run after successful bake jobs to use remaining compute time
post_bake = Shell(
    commands = [
        "echo 'post bake steps!'"
    ]
)

# =============================================================================
# go!

strider = Strider(provisioner=provisioner, pre_bake=pre_bake, post_bake=post_bake).cli(instance)
