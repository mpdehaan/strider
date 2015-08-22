
class memoize:

  def __init__(self, fn):

    self.fn = fn
    self.result = {}

  def __call__(self, *args):

    try:
        return self.result[args]
    except KeyError:
        self.result[args] = self.fn(*args)
    return self.result[args]
