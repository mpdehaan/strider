# Copyright 2015 Michael DeHaan <michael.dehaan/gmail>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import boto
import boto.ec2
import boto.ec2.blockdevicemapping
import socket
import time
from strider.common.instance_data import InstanceData, SshData
import strider.common.logger

class EC2(object):

    # TODO: remove _instance_id hack if possible

    def __init__(self, name=None, region=None, access_key_id=None,
        secret_access_key=None, security_token=None, image_id=None,
        instance_type=None, key_name=None, security_groups=None, subnet_id=None,
        ssh=None, user_data=None, tags=None, instance_profile_name=None,
        block_device_map=None, bake_name=None, bake_description=None,
        profile_name=None):

        self.name = name
        self.region = region
        self.access_key_id = access_key_id
        self.region = region
        self.secret_access_key = secret_access_key
        self.security_token = security_token
        self.image_id = image_id
        self.instance_type = instance_type
        self.key_name = key_name
        self.security_groups = security_groups
        self.subnet_id = subnet_id
        self.ssh = ssh
        self.user_data = user_data
        self.tags = tags
        self.instance_profile_name = instance_profile_name
        self.block_device_map = block_device_map
        self.bake_name = bake_name
        self.bake_description = bake_description
        self.profile_name = profile_name

        # utility instances
        self.log = strider.utils.logger.get_logger('EC2')

        # check for required args
        if not self.name:
            raise Exception("'name' is required")
        if not self.instance_type:
            raise Exception("'instance_type' is required")
        if self.tags and type(self.tags) != dict:
            raise Exception("expecting 'tags' to be a dictionary")
        if type(self.ssh) != dict:
            raise Exception("expecting 'ssh' to be a dictionary")
        if not self.security_groups:
            raise Exception("'security_groups' are required")

        # coerce inputs
        self.tags['Name'] = self.name
        self.block_device_map = self._transform_block_device_map()
        self.connection = self._connect()

    # --------------------------------------------------------------------------
    # PUBLIC VIRT API INTERFACE
    # --------------------------------------------------------------------------

    def exists(self):
        """ Is the requested instance available?  If no, spun it up. """
        return self.describe().present

    # --------------------------------------------------------------------------

    def describe(self):
        """ Return details about the instance.  Standardized between cloud providers """

        details = self._details()
        if details is None:
            return InstanceData(present=False)
        else:
            username = self.ssh['username']
            private_key_path = self.ssh['private_key_path']
            public_ip = self.ssh.get('public_ip', True)
            port = self.ssh.get('port', 22)
            host = details.ip_address
            if not public_ip:
                host = details.private_ip_address
            ssh_data = SshData(keyfile=private_key_path, user=username, host=host, port=port)
            return InstanceData(present=True, provider_specific=details, ssh=ssh_data)

    # --------------------------------------------------------------------------

    def bake(self):
        """ Create cloud images from an already running instance """

        self.log("baking AMI")
        instance_id = self.describe().provider_specific.id
        ami_id = self.connection.create_image(instance_id, self.bake_name,
            self.bake_description, no_reboot=True,
            block_device_mapping=self.block_device_map)
        self.log("AMI ID: %s" % ami_id)
        return ami_id

    # --------------------------------------------------------------------------

    def up(self):
        """ Instantiate instances if needed, otherwise just start them """

        self.log("determining if we need to create an instance")
        me = self.describe().provider_specific
        if me is None:
            self.log("creating an instance")
            reservation = self.connection.run_instances(
                image_id = self.image_id, min_count = 1, max_count = 1,
                key_name = self.key_name, user_data = self.user_data,
                addressing_type = None, subnet_id = self.subnet_id,
                instance_type = self.instance_type,
                instance_profile_name = self.instance_profile_name,
                security_group_ids = self.security_groups,
                block_device_map = self.block_device_map
            )
            self.log("instance created")
            self._tag_instances(reservation)
            self._start_instances(reservation)
        else:
            self.log("instance already exists, starting if needed")
            self.connection.start_instances([me.id])

        me = self.describe()
        if not me.present:
            raise Exception("unexpectedly can't find the instance.")

    # --------------------------------------------------------------------------

    def destroy(self):
        """ Destroy the described instance """

        self.log("looking for instances to destroy")
        me = self.describe()
        if me.present:
            self.log("destroying instance")
            self.connection.terminate_instances(instance_ids=[me.provider_specific.id])
            self.log("instance destroyed")
        else:
            self.log("no instance found to destroy")

    # --------------------------------------------------------------------------
    # PRIVATE FUNCTIONS
    # --------------------------------------------------------------------------

    def _connect(self):
        """ Connect to the cloud provider, raising an exception on failure """
        self.log("connecting...")
        conn = boto.ec2.connect_to_region(
            self.region,
            aws_access_key_id = self.access_key_id,
            aws_secret_access_key = self.secret_access_key,
            security_token = self.security_token,
            profile_name = self.profile_name
        )
        self.log("connected")
        return conn

    # --------------------------------------------------------------------------

    def _details(self):
        """ Return the cloud provider's info about the described instance"""

        reservations = self.connection.get_all_instances(
            instance_ids=None, filters=None, dry_run=False, max_results=None)

        # find the first matching instance that is not terminating/terminated
        for reservation in reservations:
            for instance in reservation.instances:
                if "Name" in instance.tags and instance.tags["Name"] == self.name:
                    if instance.state not in [ 'terminating', 'terminated', 'pending', 'shutting-down' ]:
                        return instance
        return None

    # --------------------------------------------------------------------------

    def _start_instances(self, reservation):
        """ Start the instances, harmless if not already running. """

        self.log("starting instance")
        instance_ids = [ x.id for x in reservation.instances ]
        self.connection.start_instances(instance_ids, dry_run=False)
        self.log("waiting for instance to start: %s (waiting 10 seconds...)" % instance_ids)
        while True:
            time.sleep(10)
            reservations = self.connection.get_all_instances(instance_ids=instance_ids)
            for reservation in reservations:
                for instance in reservation.instances:
                    if instance.state == 'running':
                        self.log("instance has started")
                        return

    # --------------------------------------------------------------------------

    def _transform_block_device_map(self):
        """ Reformat the user-friendly device map from striderfile into something boto likes """

        if self.block_device_map is None:
            return None
        bdm = boto.ec2.blockdevicemapping.BlockDeviceMapping()
        for (k,v) in self.block_device_map.iteritems():
            bdm[k] = boto.ec2.blockdevicemapping.EBSBlockDeviceType()
            bdm[k].size = v['size']
            for prop in [ 'ephemeral_name', 'no_device', 'volume_id',
                'snapshot_id', 'status', 'attach_time', 'delete_on_termination',
                'size', 'volume_type', 'iops', 'encrypted' ]:
                if prop in v:
                    self.log("EBS property: %s => %s" % (prop, v[prop]))
                    setattr(bdm[k], prop, v[prop])
        return bdm

    # --------------------------------------------------------------------------

    def _tag_instances(self, reservation):
        """ Apply specified tags to the instances """

        self.log("tagging instance, tags=%s" % self.tags)
        for instance in reservation.instances:
            self.connection.create_tags([instance.id], self.tags)
        self.log("tagging complete")
