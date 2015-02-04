class Listener(object):
    def notify(self, stats, duration):
        raise NotImplementedError
