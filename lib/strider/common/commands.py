# (C) Michael DeHaan, 2015, michael.dehaan@gmail.com
# LICENSE: APACHE 2

from strider.common.logger import get_logger
import os

def invoke(cmd):
    """ log a command, run it, fail if it fails """
    log = get_logger('SHELL')
    log(cmd)
    rc = os.system(cmd)
    if not rc == 0:
        log("command failed, rc: %s" % rc)
        raise Exception("boom")
