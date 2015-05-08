import logging
import time
import threading

import futures
from jnpr.junos import Device

from jnpr_nr_plugin.utils import utils


LOGGER = logging.getLogger(__name__)


class DeviceManager(object):
    def __init__(self, config):
        self.config = config
        self.active_devices = list()
        self.host_ip_map = dict()

    def find_all_devices(self, device_cfg):
        devices_mp = dict()
        discovery_tp_size = self.config.get('discovery_tp_size', 5)
        devices = utils.get_device_list(device_cfg)
        with futures.ThreadPoolExecutor(discovery_tp_size) as tp_executor:
            results = {
                tp_executor.submit(
                    self.find_device,
                    device): device for device in devices}
            devices = [fut.result() for fut in futures.as_completed(results)]
            for device in devices:
                if device is not None and device.get(
                        'ip_address') not in devices_mp:
                    devices_mp[device.get('ip_address')] = device
        LOGGER.info(
            'get_all_devices, device_count [%d]', len(
                devices_mp.values()))
        self.active_devices = devices_mp.values()
        return self.active_devices

    def get_host_name(self, device):
        if device in self.host_ip_map:
            return self.host_ip_map[device]
        return device

    def get_devices(self):
        return self.active_devices

    def find_device(self, device):
        device_addr = device.get('ip_address')
        LOGGER.debug('__find_device, [%s]', device_addr)
        dev = self.get_connected_device('self', device)
        if dev is not None:
            simulator = self.config.get('Simulator', False)
            hostname = device_addr
            if not simulator:
                hostname = utils.get_host_name(device_addr)
            self.host_ip_map[device_addr] = hostname
            LOGGER.info('__find_device, [%s=%s]', device_addr, hostname)
            self.close_connected_device('self', dev)
            return device
        return None

    def get_connected_device(self, requester_name, device):
        LOGGER.debug('get_connected_device, request by [%s]', requester_name)
        time1 = time.time()
        dev_name = device.get('ip_address')
        password_encoded = self.config.get('password_encoded', False)
        if password_encoded:
            pwd = utils.decrypt_passwd(device.get('password'))
        else:
            pwd = device.get('password')
        try:
            dev = Device(host=dev_name, user=device.get('user'),
                     password=pwd, port=device.get('port', 22), gather_facts=False, auto_probe=5)
            rpc_timeout = self.config.get('rpc_timeout', 1) * 60
            dev.open()
            if dev.connected:
                dev.timeout = rpc_timeout
                return dev
        except Exception as e:
            LOGGER.error(
                    'connect, for device [%s, %s] failed',
                    dev_name,
                    e)
        finally:
            LOGGER.debug(
                    'connect, for device %s %d(s)',
                    dev_name,
                    (time.time() - time1))
        return None

    @staticmethod
    def close_connected_device(requester_name, device):
        LOGGER.debug('close_connected_device, request by [%s]', requester_name)
        try:
            if device is not None:
                device.close()
        except Exception as e:
            LOGGER.exception('close_device, failed [%s]', e)
