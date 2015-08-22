# Main API entry point for strider
# LICENSE: APACHE 2
# (C) Michael DeHaan, 2015, michael.dehaan@gmail.com

import argparse
import traceback

class Strider(object):
    """ Main API entry point """

    __SLOTS__ = [ 'provisioner']

    def __init__(self, provisioner, pre_bake=None, post_bake=None):
        self.provisioner = provisioner
        self.pre_bake = pre_bake
        self.post_bake = post_bake

    def up(self, instances):
        """ Spin up instances, destroying them on cloud error, and then configure them """
        failed = False
        for instance in instances:
            try:
                instance.up()
            except:
                failed=True
                traceback.print_exc()
                instance.destroy()
            else:
                self.provision([instance])
            if failed:
                raise Exception("up failed")

    def provision(self, instances):
        """ (Re)configure instances that are already spun up """
        for instance in instances:
            instance_data = instance.describe()
            self.provisioner.converge(instance_data)

    def destroy(self, instances):
        """ Terminate instances """
        for instance in instances:
            instance.destroy()

    def ssh(self, instances):
        """ SSH into instance(s), one at a time """
        for instance in instances:
            instance_data = instance.describe()
            self.provisioner.ssh(instance_data)

    # FIXME: auto_teardown should be a mode, not a boolean
    def bake(self, instances, auto_teardown=False):
        """ Internal: Produce cloud images """
        for instance in instances:
            self.up([instance])
            try:
                instance_data = instance.describe()
                if self.pre_bake:
                    self.pre_bake.converge(instance_data)
                instance.bake()
                if self.post_bake:
                    self.post_bake.converge(instance_data)
            finally:
                if auto_teardown:
                    instance.destroy()

    def cli(self, instances):
        """ Main CLI entry point """
        parser = argparse.ArgumentParser(description="Dev VM Manager, expects one of the following flags:")
        parser.add_argument("--up", action="store_true", help="launch VMs")
        parser.add_argument("--provision", action="store_true", help="reconfigure VMs")
        parser.add_argument("--ssh", action="store_true", help="open a shell")
        parser.add_argument("--destroy", action="store_true", help="destroy VMs")
        parser.add_argument("--bake", action="store_true", help="bake cloud images")
        parser.add_argument("--auto-teardown", action="store_true", help="used with --bake to automatically --destroy produced VMs")
        args = parser.parse_args()

        if args.bake:
            self.bake(instances, auto_teardown=args.auto_teardown)
        elif args.up:
            self.up(instances)
        elif args.provision:
            self.provision(instances)
        elif args.ssh:
            self.ssh(instances)
        elif args.destroy:
            self.destroy(instances)
        else:
            parser.print_help()
