# (C) Michael DeHaan, 2015, michael.dehaan@gmail.copy_from
# LICENSE: APACHE 2

from strider.logger import log
import os

class Shell(object):

    __SLOTS__ = [ 'copy_from', 'copy_to', 'playbook_path', 'commands' ]

    def __init__(self, **kwargs):
        # construct everything defaulted to None
        for x in self.__SLOTS__:
            setattr(self, x, None)
        for (x,y) in kwargs.iteritems():
            setattr(self, x, y)

    def _ssh_params(self, instance_data):
        """ builds common SSH params used by both normal commands and rsync """
        (keyfile, user, host, port) = instance_data['ssh']
        return "-o Port=%s -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no" % instance_data.get('port', 22)

    def _build_ssh_cmd(self, instance_data, what):
        """ builds a shell command line """
        (keyfile, user, host, port) = instance_data['ssh']
        base = "ssh %s -i %s %s@%s -p %s" % (self._ssh_params(instance_data), keyfile, user, host, port)
        if what is None or what == "":
            return base
        return "%s %s" % (base, what)

    def _build_rsync_cmd(self, instance_data):
        """ builds a rsync command line """
        (keyfile, user, host, port) = instance_data['ssh']
        return "rsync -avze 'ssh %s -i %s' %s %s@%s:%s" % (self._ssh_params(instance_data), keyfile, self.copy_from, user, host, self.copy_to)

    def ssh(self, instance_data):
        """ open a shell into a box """
        cmd = self._build_ssh_cmd(instance_data,"")
        os.system(cmd)

    def _do_or_die(self,cmd):
        """ log a command, run it, fail if it fails """
        log("SHELL: %s" % cmd)
        rc = os.system(cmd)
        if not rc == 0:
            log("SHELL: command failed, rc: %s" % rc)
            raise Exception("boom")

    def converge(self, instance_data):
        """ rsync if needed, then run the shell commands """
        if self.copy_from:
            self._do_or_die(self._build_rsync_cmd(instance_data))
        for pc in self.commands:
            self._do_or_die(self._build_ssh_cmd(instance_data, " %s" % pc))

