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
