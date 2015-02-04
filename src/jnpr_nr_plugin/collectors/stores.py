from datetime import datetime


class StatsStore(object):
    def __init__(self):
        self.value = None
        self.min = None
        self.max = None

    def process(self, value):
        self.format(value)
        if self.min is None:
            self.min = self.value
        if self.max is None:
            self.max = self.value
        self.min = min(self.value, self.min)
        self.max = max(self.value, self.max)
        return True

    def format(self, value):
        self.value = float(value)

    def as_dict(self):
        value = self.value
        if value is None:
            value = 0
        return {'total': value, 'count': 1}


class GaugeStore(StatsStore):
    def __init__(self):
        super(GaugeStore, self).__init__()


class RateStore(StatsStore):
    def __init__(self):
        super(RateStore, self).__init__()
        self.prev_val = None
        self.prev_time = None

    def process(self, value):
        value = float(value)
        curr_time = datetime.now()
        rate_average = 0
        if self.prev_val and self.prev_time and self.prev_time < curr_time:
            # Abnormal overflow or reset of counters
            if value < self.prev_val:
                self.prev_val = None
            else:
                rate_average = (value - self.prev_val) / \
                               (curr_time - self.prev_time).total_seconds()
        is_first_time = self.prev_val is None
        self.prev_time = curr_time
        self.prev_val = value
        if not is_first_time:
            return super(RateStore, self).process(rate_average)
        return False


class CountStore(StatsStore):
    def __init__(self):
        super(CountStore, self).__init__()

    def process(self, value=1):
        if self.value:
            self.value += 1
        else:
            self.value = 1
        return True

    def format(self, value):
        self.value = int(value)


class StatsHolder(object):
    def __init__(self, name, val, unit, stat_type):
        self.name = name
        self.val = val
        self.unit = unit
        self.type = stat_type.title()
