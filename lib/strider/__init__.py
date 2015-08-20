# Main API entry point for strider
# LICENSE: APACHE 2
# (C) Michael DeHaan, 2015, michael.dehaan@gmail.com

import argparse

class Strider(object):
    """ Main API entry point """

    __SLOTS__ = [ 'provisioner']

    def __init__(self, provisioner):
        self.provisioner = provisioner

    def up(self, instances):
        """ Spin up instances, destroying them on cloud error, and then configure them """
        try:
            [ x.up() for x in instances ]
        except:
            self.destroy(instances)
            raise Exception("'up' failed")
        else:
            # TODO: flag to optionally destroy instances if this fails might be nice
            return self.provision(instances)

    def provision(self, instances):
        """ (Re)configure instances that are already spun up """
        return [ self.provisioner.converge(x.describe()) for x in instances ]

    def destroy(self, instances):
        """ Terminate instances """
        return [ x.destroy() for x in instances ]

    def ssh(self, instances):
        """ SSH into instance(s), one at a time """
        return [ self.provisioner.ssh(x.describe()) for x in instances ]

    def bake(self, instances):
        """ Produce cloud images """
        self.up(instances)
        return [ x.bake() for x in instances ]

    def cli(self, instances):
        """ Main CLI entry point """
        parser = argparse.ArgumentParser(description="Dev VM Manager, expects one of the following flags:")
        parser.add_argument("--up", action="store_true", help="launch VMs")
        parser.add_argument("--provision", action="store_true", help="reconfigure VMs")
        parser.add_argument("--ssh", action="store_true", help="open a shell")
        parser.add_argument("--destroy", action="store_true", help="destroy VMs")
        parser.add_argument("--bake", action="store_true", help="bake cloud images")
        args = parser.parse_args()
 
        if args.bake:
            self.bake(instances)
        if args.up:
            self.up(instances)
        elif args.provision:
            self.provision(instances)
        elif args.ssh:
            self.ssh(instances)
        elif args.destroy:
            self.destroy(instances)
        else:
            parser.print_help()
            

