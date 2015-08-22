
def get_logger(prefix):
    def log(msg):
        print "%s: %s" % (prefix, msg)
    return log
