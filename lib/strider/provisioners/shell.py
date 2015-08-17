# (C) Michael DeHaan, 2015, michael.dehaan@gmail.copy_from
# LICENSE: APACHE 2

from strider.logger import log
import os

class Shell(object):

    __SLOTS__ = [ 'copy_from', 'copy_to', 'playbook_path', 'commands' ]

    def __init__(self, **kwargs):
        for (x,y) in kwargs.iteritems():
            setattr(self, x, y)

    def converge(self, instance_data):

        (keyfile, user, host, port) = instance_data['ssh']
        ssh_basic = "ssh -i %s %s@%s -p %s " % (keyfile, user, host, port)

        ## Rsync bits

        # FIXME: don't ignore port
        rsync_cmd = "rsync -avze 'ssh -i %s' %s %s@%s:%s" % (keyfile, self.copy_from, user, host, self.copy_to)
        log("ANSIBLE: %s" % rsync_cmd)
        rc = os.system(rsync_cmd)
        if not rc == 0:
            log("rsync failed, rc: %s" % rc)
            raise Exception("boom")

        ## Run commands
        
        for pc in self.commands:
            prep_cmd = ssh_basic + " %s" % pc
            log("ANSIBLE: %s" % prep_cmd)
            rc = os.system(prep_cmd)
            if not rc == 0:
                log("prep cmd failed, rc: %s" % rc)
                raise Exception("boom")

