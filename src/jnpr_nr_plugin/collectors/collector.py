import threading
import logging

import futures

import stores


LOGGER = logging.getLogger(__name__)


class StatsCollector(object):
    def __init__(self, config, device_mgr):
        self.config = config
        self.device_mgr = device_mgr
        self.pending_request = list()
        self.stats = dict()
        self.stats_store = dict()
        self.lock = threading.Lock()
        self.listeners = list()

    def add_listener(self, listener):
        self.listeners.append(listener)

    def collect(self):
        try:
            LOGGER.debug('collect, start')
            enabled = self.config.get('enable', True)
            if not enabled:
                LOGGER.warn(
                    'collect, data collection is disabled')
                return
            tp_size = self.config.get('tp_size', 5)
            with futures.ThreadPoolExecutor(tp_size) as tp_executor:
                for device in self.device_mgr.get_devices():
                    future = tp_executor.submit(self.collect_data, device)
                    self.pending_request.append(future)
                    future.add_done_callback(self.collect_datacb)
                futures.wait(self.pending_request)
            if LOGGER.isEnabledFor(logging.DEBUG):
                self.dump()
            for listener in self.listeners:
                listener.notify(self.stats, self.poll_time())
            self.clear()
        except Exception as e:
            LOGGER.exception('collect, failed %s', e)
        finally:
            LOGGER.debug('collect, end')

    def collect_data(self, device):
        dev_name = device.get('ip_address')
        results = list()
        dev = None
        try:
            LOGGER.info('collect_data, start [%s]', dev_name)
            dev = self.device_mgr.get_connected_device(self.name(),
                                                       device)
            if dev is None:
                return dev_name, results
            for cmd in self.getcmds():
                results.append(self.executecmd(dev_name, dev, cmd))
        except Exception as e:
            LOGGER.exception('collect_data failed [%s,%s]', dev_name, e)
        finally:
            self.device_mgr.close_connected_device(self.name(), dev)
            LOGGER.debug('collect_data, end [%s]', dev_name)
        return dev_name, results

    def collect_datacb(self, future):
        device = ''
        try:
            device, cmd_results = future.result()
            LOGGER.debug('collect_data_cb, start for device [%s]', device)
            for cmd_res in cmd_results:
                self.processcmd(device, cmd_res)
        except Exception as e:
            LOGGER.exception('collect_data_cb, failed [%s]', e)
        finally:
            LOGGER.info(
                'collect_data_cb, complete for device [%s]',
                device)

    def poll_time(self):
        poll_time = self.config.get('poll_interval')
        return poll_time

    def clear(self, is_stop=False):
        self.pending_request = list()
        if is_stop:
            self.stats_store.clear()
        else:
            for v in self.stats_store.values():
                for stats in v.values():
                    stats.value = None
        self.stats.clear()

    def update_stats(self, dev_name, holder):
        if holder is None:
            return
        device = self.device_mgr.get_host_name(dev_name)
        with self.lock:
            if device not in self.stats_store:
                self.stats_store[device] = dict()
            if device not in self.stats:
                self.stats[device] = dict()
        d_stats_store = self.stats_store[device]
        if holder.name not in d_stats_store:
            d_stats_store[
                holder.name] = getattr(
                stores, holder.type + 'Store')()
        if holder.name not in self.stats and holder.type == 'Count':
            d_stats_store[
                holder.name] = getattr(
                stores,
                holder.type + 'Store')()
        stats = d_stats_store[holder.name]
        if stats.process(holder.val):
            self.stats[device][holder.name] = stats.as_dict()

    def summarize(self, dev_name, paths):
        device = self.device_mgr.get_host_name(dev_name)
        if device not in self.stats or paths is None:
            return
        d_stats_store = self.stats_store[device]
        for path, unit in paths:
            d_summary_elements = [(k, v) for k, v in d_stats_store.items() if k.startswith(path)]
            if len(d_summary_elements) > 0:
                k, v = d_summary_elements[0]
                if isinstance(v, stores.CountStore):
                    continue
                is_average = isinstance(v, stores.GaugeStore)
                count = 0
                value = 0.0
                for key, store in d_summary_elements:
                    if store.value is not None:
                        value += store.value
                        count += 1
                if count == 0:
                    continue
                if is_average:
                    value = value / count
                if path.endswith('/'):
                    path = path[0:len(path) - 1]
                path = '%s/summary/%s' % (path[0:path.find('/')], path[path.find('/') + 1:len(path)])
                holder = stores.StatsHolder(path + unit, value, '', 'gauge')
                self.update_stats(device, holder)

    def dump(self):
        for device, dev_stats in self.stats.items():
            for key, val in dev_stats.items():
                LOGGER.debug(
                    'dump_stats, for device %s %s=%s ',
                    device,
                    key,
                    str(val))

    def name(self):
        return 'StatsCollector'

    def getcmds(self):
        return list()

    def executecmd(self, device, dev_obj, cmd):
        raise NotImplementedError

    def processcmd(self, device, cmd_response):
        raise NotImplementedError