from datetime import datetime, time
import pprint
from time import mktime


def print_config(config):
    confdict = {section: dict(config.items(section)) for section in config.sections()}
    pprint.PrettyPrinter().pprint(confdict)


class IntervalTrigger(object):

    def __init__(self, last_checked, interval):
        self.last_checked = last_checked
        self.interval = interval
        self.triggered_manually = False

    def get_current_timestamp(self):
        return mktime(datetime.now().timetuple())

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


def parse_csv_times(times_list_str):
    if times_list_str is None:
        return []

    times_splits = times_list_str.strip().split(',')

    times = []
    invalid = []

    for time_split in times_splits:
        if not time_split:
            continue

        parts = time_split.strip().split(':')
        hour = None
        minute = 0

        if len(parts) > 0:
            try:
                hour = int(parts[0])
            except ValueError:
                pass

        if len(parts) > 1:
            try:
                minute = int(parts[1])
            except ValueError:
                pass

        if hour is None:
            invalid.append(time_split)
            continue

        times.append(time(hour=hour, minute=minute))

    return times, invalid
