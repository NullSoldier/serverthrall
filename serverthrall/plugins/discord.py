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
        config.set_default('force_test_discord', False)
        config.set_default('interval.interval_seconds', self.ONE_MINUTE)
        config.queue_save()
        self.failed_queue = []
        self.is_ready = False

    def ready(self, *args, **kwargs):
        super(Discord, self).ready(*args, **kwargs)
        self.is_ready = True
        self.try_failed_messages()

        if self.config.getboolean('force_test_discord'):
            self.config.set('force_test_discord', False)
            self.config.queue_save()
            self.send_test_messages()

    def tick_interval(self):
        self.try_failed_messages()

    def send_message(self, key, message):
        if not self.enabled:
            return

        if not self.config.has_option(key):
            self.logger.debug("Dropping message because key %s isnt set: %s" % (key, message))
            return False

        if not self.is_ready:
            self.failed_queue.insert(0, (key, message, datetime.now()))
            return

        self.logger.debug("Sending to discord in %s: %s" % (key, message))
        webhook_urls = self.config.get(key, default='').strip().split(';')
        all_success = True

        for webhook_url in webhook_urls:
            if not webhook_url:
                continue

            sent_successfully = self._send_message(webhook_url, message)

            if not sent_successfully:
                self.failed_queue.insert(0, (webhook_url, message, datetime.now()))
                all_success = False

        return all_success

    def _send_message(self, webhook_url, message):
        if not self.enabled:
            return False

        try:
            response = requests.post(
                url=webhook_url,
                json={'content': message})
        except ConnectionError:
            self.logger.debug("Failed to send message because of connection error")
            return False
        except Exception:
            self.logger.exception('Error when sending discord message')

        if response.status_code < 200 and response.status_code >= 300:
            self.logger.debug("Failed to send message with response " + response.status_code)
            return False

        return True

    def try_failed_messages(self):
        stale_config = self.config.getint('stale_message_seconds')
        threshold = datetime.now() - timedelta(seconds=stale_config)
        failed_count = len(self.failed_queue)

        if failed_count == 0:
            return

        i = failed_count - 1
        while i >= 0:
            webhook_url, message, created_time = self.failed_queue[i]

            if created_time < threshold:
                self.logger.debug("Destroying discord message that is too old " + message)
                del self.failed_queue[i]

            else:
                was_successful = self._send_message(webhook_url, message)
                if was_successful:
                    del self.failed_queue[i]

            i -= 1

    def send_test_messages(self):
        for key in self.config.options():
            value = self.config.get(key)

            if not value.startswith('http'):
                continue

            is_success = self.send_message(key, 'Hello from ServerThrall')

            if not is_success:
                self.logger.warning('%s webhook failed to send.' % key)
