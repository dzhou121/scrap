def chunks(l, n):
    """ split list l into chunks of size n. """
    return [l[i:i+n] for i in xrange(0, len(l), n)]
