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

import strider.utils.logger
from strider.common.commands import invoke
from strider.common.instance_data import InstanceData
import os
import socket
import time

SSH_CANARY = "_ssh_availability_test_"
SSH_RETRY = 10
SSH_CONNECT_TIMEOUT = 10

class Shell(object):

    def __init__(self, copy_from=None, copy_to=None, commands=None):

        self.log = strider.utils.logger.get_logger('SHELL')
        self.copy_from = copy_from
        self.copy_to = copy_to
        self.commands = commands
        self.waited = False
        if self.commands is None:
            self.commands = []

    # --------------------------------------------------------------------------
    # PROVISIONER PUBLIC API
    # --------------------------------------------------------------------------

    def _wait_for_ready(self, instance_data):
        """ wait for SSH availability """

        if self.waited:
            return True

        (host, port) = (instance_data.ssh.host, instance_data.ssh.port)
        self.log("checking for SSH availability on %s:%s" % (host, port))
        while True:

            cmd = self._build_ssh_cmd(
                instance_data,
                "echo %s" % SSH_CANARY,
                connect_timeout=SSH_CONNECT_TIMEOUT)
            output = invoke(cmd, check_output=True).strip()

            if output.endswith(SSH_CANARY):
                self.waited = True
                return True

            self.log("retrying SSH availability in %s seconds..." % SSH_RETRY)
            time.sleep(SSH_RETRY)

    def ssh(self, instance_data):
        """ open a shell into a box """

        self._wait_for_ready(instance_data, extra_sleep=0)
        return invoke(self._build_ssh_cmd(instance_data,""))

    def converge(self, instance_data):
        """ rsync if needed, then run the shell commands """

        self._wait_for_ready(instance_data)
        if self.copy_from:
            invoke(self._build_rsync_cmd(instance_data))
        for pc in self.commands:
            invoke(self._build_ssh_cmd(instance_data, " %s" % pc))

    # --------------------------------------------------------------------------
    # PRIVATE FUNCTIONS
    # --------------------------------------------------------------------------

    def _ssh_params(self, instance_data):
        """ builds common SSH params used by both normal commands and rsync """

        return "-o Port=%s -o LogLevel=quiet -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no" % instance_data.ssh.port

    def _build_ssh_cmd(self, instance_data, what, connect_timeout=30):
        """ builds a shell command line """

        base = "ssh %s -o ConnectTimeout=%s -i %s %s@%s -p %s" % (
            self._ssh_params(instance_data),
            connect_timeout,
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
