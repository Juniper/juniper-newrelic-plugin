import importlib
import logging
import sys
import time

from helper import parser
import helper
import futures

from jnpr_nr_plugin.device import device_mgr
from jnpr_nr_plugin.nr import nrproxy
from jnpr_nr_plugin.utils import utils


LOGGER = logging.getLogger('jnpr_nr_plugin.' + __name__)


class Controller(helper.Controller):
    def __init__(self, args, operating_system):
        super(Controller, self).__init__(args, operating_system)
        self.collectors = list()
        self.app_config = self.config.application
        self.next_wake_interval = self.app_config.get(
            'poll_interval',
            5) * 60
        self._wake_interval = self.next_wake_interval

    def setup(self):
        LOGGER.info('setup, start discovery')
        manager = device_mgr.DeviceManager(self.app_config.get('DeviceMgr'))
        nr_proxy = nrproxy.NRProxy(self.app_config.get('NRProxy'))
        devices = manager.find_all_devices(
            self.config.application.get('Devices'))
        if len(devices) == 0:
            LOGGER.error('setup, no devices successfully discovered')
            sys.exit(1)
        configs = self.app_config.get('Collectors')
        for config in configs.keys():
            mdl_index = config.rfind('.')
            collector_handle = getattr(
                importlib.import_module(config[0:mdl_index]), config[mdl_index + 1:len(config)])
            configs[config]['poll_interval'] = self._wake_interval
            collector = collector_handle(
                configs[config], manager)
            collector.add_listener(nr_proxy)
            self.collectors.append(collector)
        LOGGER.info('setup, end discovery')

    @property
    def wake_interval(self):
        return self.next_wake_interval

    def process(self):
        LOGGER.warn('process, start ')
        start_time = time.time()
        with futures.ThreadPoolExecutor(len(self.collectors)) as tp_executor:
            results = {
                tp_executor.submit(
                    collector.collect): collector for collector in self.collectors}
            futures.as_completed(results)
        duration = time.time() - start_time
        self.next_wake_interval = self._wake_interval - duration
        if self.next_wake_interval < 1:
            LOGGER.warn('process, poll interval took greater than %is',
                        duration)
            self.next_wake_interval = int(self._wake_interval)
        LOGGER.warn('process, end in %.2fs, next poll will begin at %is from now',
                    duration, self.next_wake_interval)

    def shutdown(self):
        LOGGER.info('shutdown, start')
        retries = self.app_config.get('shutdown_retries', 3)
        sleep_time = self.app_config.get('shutdown_waittime', 0.5) * 60

        while self.is_active and retries > 0:
            time.sleep(sleep_time)
            retries -= 1

        LOGGER.info('shutdown, end')

    def on_sigusr1(self, signal, frame):
        utils.dump_stack(signal, frame, LOGGER)


def main():
    parser.name('jnpr_nr_plugin')
    parser.description('jnpr_nr_plugin')
    helper.start(Controller)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
