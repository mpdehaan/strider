# (C) Michael DeHaan, 2015, michael.dehaan@gmail.copy_from
# LICENSE: APACHE 2

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
        return [ self.destroy(x) for x in instances ]
