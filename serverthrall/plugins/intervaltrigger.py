from datetime import datetime
import time


class IntervalTrigger(object):

    def __init__(self, last_checked, interval):
        self.last_checked = last_checked
        self.interval = interval
        self.triggered_manually = False

    def get_current_timestamp(self):
        return time.mktime(datetime.now().timetuple())

    def trigger(self):
        self.triggered_manually = True

    def is_ready(self, extra_seconds=0):
        if self.triggered_manually:
            return True

        current = self.get_current_timestamp()
        delta = current - self.last_checked
        return delta >= (self.interval + extra_seconds)

    def reset(self):
        self.last_checked = self.get_current_timestamp()
        self.triggered_manually = False
