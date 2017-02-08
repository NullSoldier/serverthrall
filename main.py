# flake8: noqa
from manager.daemon import Daemon
from manager.config import save_config
import atexit

def teardown():
	save_config(daemon.config)
	daemon.teardown()

atexit.register(teardown)

daemon = Daemon()
daemon.run()