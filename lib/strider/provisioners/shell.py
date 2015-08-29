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

SSH_CANARY = "_ssh_availability_test_"  # string used in SSH connectivity checks
SSH_RETRY = 10                          # how long to wait per check iteration
SSH_CONNECT_TIMEOUT = 10

class Shell(object):

    def __init__(self, copy_from=None, copy_to=None, commands=None):

        self.log = strider.utils.logger.get_logger('SHELL')

        self.copy_from = copy_from
        self.copy_to = copy_to

        self.commands = commands

        # track whether we've waited for SSH yet
        self.waited = False

        if self.commands is None:
            self.commands = []

        # backwards compatibility
        if self.copy_from and self.copy_to:
            log("WARNING: copy_from and copy_to are deprecated, see the new example on github")
            self.commands.insert(0, dict(
                type = "copy",
                copy_from = self.copy_from,
                copy_to = self.copy_to
            ))

    # --------------------------------------------------------------------------
    # PROVISIONER PUBLIC API
    # --------------------------------------------------------------------------

    def ssh(self, instance_data):
        """ open a shell into a box """

        # if writing a new provisioner, it may be helpful to subclass this
        # class rather than reimplementing this method.  Then just override
        # converge

        self._wait_for_ready(instance_data)
        return invoke(self._build_ssh_cmd(instance_data,""))

    # --------------------------------------------------------------------------

    def converge(self, instance_data):
        """ run all convergence operations in the commands list """

        for item in self.commands:
            if isinstance(item, basestring):
                item = dict(type="ssh", command=item)
            self._dispatch(instance_data, item)

    # --------------------------------------------------------------------------
    # PRIVATE FUNCTIONS
    # --------------------------------------------------------------------------

    def _dispatch(self, instance_data, item):
        """
        Handle an item in the commands array, examples:

        "echo foo"                           # SSH (shorthand)
        { type: "ssh", command: "echo foo"}  # also SSH
        { type: "copy", from: x, to: y }     # scp

        """

        what = item.get('type', None)

        if what == 'ssh':
            # wait for SSH and then launch a command
            self._wait_for_ready(instance_data)
            return invoke(self._build_ssh_cmd(
                instance_data, item.get('command', None)
            ))

        elif what == 'copy':
            # wait for SSH and then launch an scp
            copy_from = item['copy_from']
            copy_to = item['copy_to']
            self._wait_for_ready(instance_data)
            invoke(self._build_ssh_cmd(instance_data, "mkdir -p %s" % copy_to))
            return invoke(self._build_copy_cmd(
                instance_data,
                copy_from = copy_from,
                copy_to = copy_to
            ))

        # add any other operational types here (such as local command execution)

        else:
            raise Exception("unknown type in commands list: %s, %s" % (item, what))

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

    # --------------------------------------------------------------------------

    def _ssh_params(self, instance_data):
        """ builds common SSH params used by all operations"""

        return "-o Port=%s -o LogLevel=quiet -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no" % instance_data.ssh.port

    # --------------------------------------------------------------------------

    def _build_ssh_cmd(self, instance_data, what, connect_timeout=30):
        """ builds a shell command line """

        assert instance_data is not None
        assert what is not None

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

    # --------------------------------------------------------------------------

    def _build_copy_cmd(self, instance_data, copy_from, copy_to):
        """ builds a remote copy command line """

        # previously we used rsync here but I found it was unreliable
        # on some AWS instances - even with particular userdata.  This will
        # copy more data but will fail MUCH less, making it more reliable
        # in build systems.  For CI, this is a non-issue.  Developers
        # may wish to add a "use_rsync" flag.  Pull requests would be
        # welcome.

        assert instance_data is not None
        assert copy_from is not None
        assert copy_to is not None

        return "scp -r %s -i %s -P %s %s %s@%s:%s" % (
            self._ssh_params(instance_data),
            instance_data.ssh.keyfile,
            instance_data.ssh.port,
            copy_from,
            instance_data.ssh.user,
            instance_data.ssh.host,
            copy_to
        )
