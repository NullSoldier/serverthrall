from datetime import datetime
import pytz
import tzlocal
import calendar


def parse_timestamp(timestamp):
    if not timestamp:
        return None

    utc_datetime = datetime.utcfromtimestamp(timestamp)

    return calendar.timegm(tzlocal
        .get_localzone()
        .localize(utc_datetime)
        .astimezone(pytz.utc)
        .replace(tzinfo=None)
        .timetuple())
