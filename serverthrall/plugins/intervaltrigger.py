from datetime import datetime
import time


class IntervalTrigger(object):

    def __init__(self, last_checked, interval):
        self.last_checked = last_checked
        self.interval = interval

    def get_current_timestamp(self):
        return time.mktime(datetime.now().timetuple())

    def is_ready(self):
        current = self.get_current_timestamp()
        delta = current - self.last_checked
        return delta <= self.interval

    def reset(self):
        self.last_checked = self.get_current_timestamp()
