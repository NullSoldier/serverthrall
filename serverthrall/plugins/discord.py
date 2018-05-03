from .intervaltickplugin import IntervalTickPlugin
from datetime import datetime, timedelta
from requests.exceptions import ConnectionError
import requests


class Discord(IntervalTickPlugin):

    ONE_MINUTE = 60
    TWO_MINUTES = 2 * 60

    def __init__(self, config):
        config.set_default('enabled', 'false')
        super(Discord, self).__init__(config)
        config.set_default('stale_message_seconds', self.TWO_MINUTES)
        config.set_default('interval.interval_seconds', self.ONE_MINUTE)
        config.queue_save()
        self.failed_queue = []
        self.is_ready = False

    def ready(self, *args, **kwargs):
        super(Discord, self).ready(*args, **kwargs)
        self.is_ready = True
        self.try_failed_messages()

    def tick_interval(self):
        self.try_failed_messages()

    def send_message(self, key, message):
        if not self.enabled:
            return

        if not self.is_ready:
            self.failed_queue.insert(0, (key, message, datetime.now()))
            return

        self.logger.info("Sending to discord in %s: %s" % (key, message))
        sent_successfully = self._send_message(key, message)

        if not sent_successfully:
            self.failed_queue.insert(0, (key, message, datetime.now()))

    def _send_message(self, key, message):
        if not self.enabled:
            return False

        if not self.config.has_option(key):
            self.logger.debug("Dropping message because key %s isnt set: %s" % (key, message))
            return False

        try:
            response = requests.post(
                url=self.config.get(key),
                json={'content': message})
        except ConnectionError:
            self.logger.debug("Failed to send message because of connection error")
            return False

        if response.status_code < 200 and response.status_code >= 300:
            self.logger.debug("Failed to send message with response " + response.status_code)
            return False

        return True

    def try_failed_messages(self):
        stale_config = self.config.getint('stale_message_seconds')
        threshold = datetime.now() - timedelta(seconds=stale_config)

        count = len(self.failed_queue)
        i = 0

        while i < count:
            key, message, created_time = self.failed_queue[i]

            print(created_time, threshold)

            if created_time < threshold:
                self.logger.debug("Destroying discord message that is too old " + message)
                del self.failed_queue[i]

            else:
                was_successful = self._send_message(key, message)
                if was_successful:
                    del self.failed_queue[i]

            i += 1
