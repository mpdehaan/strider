# (C) Michael DeHaan, 2015, michael.dehaan@gmail.com
# LICENSE: APACHE 2

import strider.utils.logger
from strider.common.commands import invoke
from strider.common.instance_data import InstanceData
import os
import socket
import time

class Shell(object):

    def __init__(self, copy_from=None, copy_to=None, commands=None):

        self.log = strider.utils.logger.get_logger('SHELL')
        self.copy_from = copy_from
        self.copy_to = copy_to
        self.commands = commands
        if self.commands is None:
            self.commands = []

    # --------------------------------------------------------------------------
    # PROVISIONER PUBLIC API
    # --------------------------------------------------------------------------

    # FIXME: reimplement by just calling SSH
    def wait_for_ready(self, instance_data, extra_sleep=10):

        (host, port) = (instance_data.ssh.host, instance_data.ssh.port)
        self.log("checking for SSH availability on %s:%s" % (host, port))
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((host, port))
        except socket.error as e:
            self.log("SSH not ready, waiting 10 seconds")
            time.sleep(10)
            self.log("SSH ready")
            s.close()
            # socket start isn't enough for SSH-ready sometimes
            if extra_sleep:
                time.sleep(extra_sleep)

    def ssh(self, instance_data):
        """ open a shell into a box """

        self.wait_for_ready(instance_data, extra_sleep=0)
        return invoke(self._build_ssh_cmd(instance_data,""))

    def converge(self, instance_data):
        """ rsync if needed, then run the shell commands """

        self.wait_for_ready(instance_data)
        if self.copy_from:
            invoke(self._build_rsync_cmd(instance_data))
        for pc in self.commands:
            invoke(self._build_ssh_cmd(instance_data, " %s" % pc))

    # --------------------------------------------------------------------------
    # PRIVATE FUNCTIONS
    # --------------------------------------------------------------------------

    def _ssh_params(self, instance_data):
        """ builds common SSH params used by both normal commands and rsync """

        return "-o Port=%s -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no" % instance_data.ssh.port

    def _build_ssh_cmd(self, instance_data, what):
        """ builds a shell command line """

        base = "ssh %s -i %s %s@%s -p %s" % (
            self._ssh_params(instance_data),
            instance_data.ssh.keyfile,
            instance_data.ssh.user,
            instance_data.ssh.host,
            instance_data.ssh.port
        )
        if what is None or what == "":
            return base
        return "%s %s" % (base, what)

    def _build_rsync_cmd(self, instance_data):
        """ builds a rsync command line """

        return "rsync -avze 'ssh %s -i %s' %s %s@%s:%s" % (
            self._ssh_params(instance_data),
            instance_data.ssh.keyfile,
            self.copy_from,
            instance_data.ssh.user,
            instance_data.ssh.host,
            self.copy_to
        )
