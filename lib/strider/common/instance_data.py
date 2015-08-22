# (C) Michael DeHaan, 2015, michael.dehaan@gmail.com
# LICENSE: APACHE 2

class InstanceData(object):

    __SLOTS__ = [ 'present', 'ssh' ]

    def __init__(self, present=False, provider_specific=None, ssh=None):
        
        self.present = present
        self.provider_specific = provider_specific
        self.ssh = ssh


class SshData(object):

    __SLOTS__ = [ 'keyfile', 'user', 'host', 'port' ]

    def __init__(self, keyfile=None, user=None, host=None, port=None):

        if port is None:
            port = 22
        if user is None:
            user = 'root'
        assert host is not None
        assert keyfile is not None

        self.keyfile = keyfile
        self.user = user
        self.port = port
        self.host = host
