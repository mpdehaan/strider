# (C) Michael DeHaan, 2015, michael.dehaan@gmail.copy_from
# LICENSE: APACHE 2

HAS_BOTO = False
try:
    import boto
    import boto.ec2
    HAS_BOTO = True
except ImportError:
    pass

import socket
from strider.logger import log
import time

class EC2(object):

    __SLOTS__ = [ 'name', 'region', 'access_key_id', 'secret_access_key', 'security_token',
                  'image_id', 'instance_type', 'key_name', 'security_groups', 'ssh', 'user_data',
                  'tags', "_connection" ]

    def __init__(self, **kwargs):
        if not HAS_BOTO:
            raise Exception("boto is required to use this Virt plugin")
        for x in self.__SLOTS__:
            setattr(self, x, None)
        for (x,y) in kwargs.iteritems():
            setattr(self, x, y)
        self._connection = None
        if self.tags is None:
            self.tags = dict()
            self.tags['Name'] = self.name
        # FIXME: more required argument checking
        if not self.security_groups:
            raise Exception("security_groups are required")

    # FIXME: cleanup
    def connect(self):
        if self._connection is not None:
            return self._connection
        self._connection = self._connect()
        return self._connection

    def _connect(self):
        log("EC2: establishing connection")
        conn = boto.ec2.connect_to_region(
            self.region,
            aws_access_key_id = self.access_key_id,
            aws_secret_access_key = self.secret_access_key,
            security_token = self.security_token
        )
        log("EC2: connected")
        return conn

    def exists(self):
        return self._details() is not None

    def describe(self):
        details = self._details()
        if details is None:
            return dict(present=False, provider_specific=None)
        else:
            return dict(present=True, provider_specific=details, ssh=self._get_ssh_connection(details))

    def _details(self):
        log("EC2: getting instance details")
        conn = self.connect()
        reservations = conn.get_all_instances(instance_ids=None, filters=None, dry_run=False, max_results=None)
        for reservation in reservations:
            for instance in reservation.instances:
                if "Name" in instance.tags and instance.tags["Name"] == self.name and instance.state not in [ 'terminating', 'terminated', 'pending', 'shutting-down' ]:
                    log("EC2: found instance: %s" % instance.id)
                    return instance
        return None

    def _wait_for_instances(self, instance_ids):
        conn = self.connect()
        while True:
            reservations = conn.get_all_instances(instance_ids=instance_ids)
            for reservation in reservations:
                for instance in reservation.instances:
                    if instance.state == 'running':
                        return True
            log("EC2: still waiting for instances to start (%s), sleeping 10 seconds ..." % instance_ids)
            time.sleep(10)

    def _tag_instances(self, reservation):
        """ internal: assign a name to the instances """
        log("EC2: tagging instance")
        conn = self.connect()
        for instance in reservation.instances:
            conn.create_tags([instance.id], self.tags)
        log("EC2: tagging complete")

    def _get_ssh_connection(self, instance):
        username = self.ssh['username']
        private_key_path = self.ssh['private_key_path']
        public_ip = self.ssh.get('public_ip', True)
        port = self.ssh.get('port', 22)
        if public_ip:
            log("EC2: will SSH to the public IP address: %s" % instance.ip_address)
            return (private_key_path, username, instance.ip_address, port)
        else:
            log("EC2: will SSH to the private IP address: %s" % instance.private_ip_address)
            return (private_key_path, username, instance.private_ip_address, port)

    def _wait_for_ssh(self, host, port):
        log("EC2: waiting for SSH on %s:%s" % (host, port))
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((host, port))
        except socket.error as e:
            log("EC2: SSH not ready, waiting 10 seconds")
            time.sleep(10)
        log("EC2: SSH ready")
        s.close()

    def _start_instances(self, reservation):
        log("EC2: starting instance")
        conn = self.connect()
        instance_ids = [ x.id for x in reservation.instances ]
        conn.start_instances(instance_ids, dry_run=False)
        log("EC2: start request complete")
        log("EC2: waiting for instance to start: %s" % instance_ids)
        self._wait_for_instances(instance_ids)
        log("EC2: instance has started")

    def up(self):

        log("EC2: determining if we need to create an instance")

        conn = self.connect()
        me = self._details()

        if me is None:
            log("EC2: creating an instance")
            log("EC2: key name: %s" % self.key_name)
            log("EC2: security groups: %s" % self.security_groups)
            reservation = conn.run_instances(
                image_id = self.image_id,
                min_count = 1, max_count = 1,
                key_name = self.key_name,
                user_data = self.user_data,
                addressing_type = None,
                instance_type = self.instance_type,
                security_group_ids = self.security_groups
            )
            log("EC2: instance created")
            self._tag_instances(reservation)
            self._start_instances(reservation)

        else:
            log("EC2: instance already exists, starting if needed")
            conn.start_instances([me.id])

        me = self._details()
        if me is None:
            raise Exception("EC2: can't find instance ... eventual consistency hell?")

        log("EC2: waiting on SSH ...")
        (identity, user, host, port) = self._get_ssh_connection(me)
        # TODO -- figure out why this takes so long on socket connect even if up
        self._wait_for_ssh(host, port)
        log("EC2: ready for provisioning!")

    def destroy(self):
        log("EC2: looking for instances to destroy")
        conn = self.connect()
        me = self._details()
        if me is not None:
            log("EC2: destroying instance")
            conn.terminate_instances(instance_ids=[me.id])
            log("EC2: instance destroyed")
        else:
            log("EC2: no instance found to destroy")
