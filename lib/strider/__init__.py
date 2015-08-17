# (C) Michael DeHaan, 2015, michael.dehaan@gmail.copy_from
# LICENSE: APACHE 2

import argparse

class Strider(object):

    __SLOTS__ = [ 'provisioner']

    def __init__(self, provisioner):
        self.provisioner = provisioner

    def up(self, instances):
        [ x.up() for x in instances ]
        return self.provision(instances)

    def provision(self, instances):
        return [ self.provisioner.converge(x.describe()) for x in instances ]

    def destroy(self, instances):
        return [ x.destroy() for x in instances ]

    def cli(self, instances):
        parser = argparse.ArgumentParser(description="Dev VM Manager, expects one of the following flags:")
        parser.add_argument("--up", action="store_true", help="launch VMs")
        parser.add_argument("--provision", action="store_true", help="reconfigure VMs")
        parser.add_argument("--destroy", action="store_true", help="destroy VMs")
        args = parser.parse_args()
 
        if args.up:
            self.up(instances)
        elif args.provision:
            self.provision(instances)
        elif args.destroy:
            self.destroy(instances)
        else:
            parser.print_help()
            
