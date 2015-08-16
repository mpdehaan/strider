# (C) Michael DeHaan, 2015, michael.dehaan@gmail.copy_from
# LICENSE: APACHE 2

from strider.logger import log
import os

class AnsibleSSH(object):

    __SLOTS__ = [ 'copy_from', 'copy_to', 'playbook_path', 'playbook_cmd', 'prep_cmds' ]

    def __init__(self, **kwargs):
        for (x,y) in kwargs.iteritems():
            setattr(self, x, y)

    def converge(self, instance_data):

        (keyfile, user, host, port) = instance_data['ssh']

        ## Install ansible and make directory

        ssh_basic = "ssh -i %s %s@%s -p %s " % (keyfile, user, host, port)

        for pc in self.prep_cmds:
            prep_cmd = ssh_basic + " %s" % pc
            log("ANSIBLE: %s" % prep_cmd)
            rc = os.system(prep_cmd)
            if not rc == 0:
                log("prep cmd failed, rc: %s" % rc)
                raise Exception("boom")

        ## Rsync bits

        # FIXME: don't ignore port
        rsync_cmd = "rsync -avze 'ssh -i %s' %s %s@%s:%s" % (keyfile, self.copy_from, user, host, self.copy_to)
        log("ANSIBLE: %s" % rsync_cmd)
        rc = os.system(rsync_cmd)
        if not rc == 0:
            log("rsync failed, rc: %s" % rc)
            raise Exception("boom")

        ## Run playbook

        playbook_cmd = ssh_basic + " %s" % self.playbook_cmd
        log("ANSIBLE: %s" % playbook_cmd)

        rc = os.system(playbook_cmd)
        if not rc == 0:
            log("ssh to playbook failed, rc: %s" % rc)
            raise Exception("boom")
