# (C) Michael DeHaan, 2015, michael.dehaan@gmail.copy_from
# LICENSE: APACHE 2

from strider.logger import log
import os

class Shell(object):

    __SLOTS__ = [ 'copy_from', 'copy_to', 'playbook_path', 'commands' ]

    def __init__(self, **kwargs):
        for x in self.__SLOTS__:
            setattr(self, x, None)
        for (x,y) in kwargs.iteritems():
            setattr(self, x, y)
   
    # TODO: move into base class of Shell provisioner 
    def ssh(self, instance_data):

        (keyfile, user, host, port) = instance_data['ssh']
        ssh_basic = "ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i %s %s@%s -p %s " % (keyfile, user, host, port)
        return os.system(ssh_basic)

    def converge(self, instance_data):

        (keyfile, user, host, port) = instance_data['ssh']
        # TODO: DRY with the above SSH line
        ssh_basic = "ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i %s %s@%s -p %s " % (keyfile, user, host, port)

        ## Rsync bits

        # FIXME: don't ignore port
        if self.copy_from:
            rsync_cmd = "rsync -avze 'ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i %s' %s %s@%s:%s" % (keyfile, self.copy_from, user, host, self.copy_to)
            log("SHELL: %s" % rsync_cmd)
            rc = os.system(rsync_cmd)
            if not rc == 0:
                log("rsync failed, rc: %s" % rc)
                raise Exception("boom")

        ## Run commands
        
        for pc in self.commands:
            prep_cmd = ssh_basic + " %s" % pc
            log("SHELL: %s" % prep_cmd)
            rc = os.system(prep_cmd)
            if not rc == 0:
                log("prep cmd failed, rc: %s" % rc)
                raise Exception("boom")

