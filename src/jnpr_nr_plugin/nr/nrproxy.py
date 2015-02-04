import json
import logging
import os
import socket
import zlib

import requests

from jnpr_nr_plugin.collectors import listeners


LOGGER = logging.getLogger(__name__)


class NRProxy(listeners.Listener):
    def __init__(self, config):
        self.config = config
        self.URL = 'https://platform-api.newrelic.com/platform/v1/metrics'
        self.MAX_STATS_PER_POST = self.config.get('max_stats', 8000)
        self.NAME = self.config.get('name', 'net.juniper.jnpr_nr_plugin')
        self.UID = self.NAME + '.Juniper'

    def notify(self, stats, duration):
        single_component = self.config.get('single_component', False)
        if single_component:
            all_stats = dict()
            for comp, comp_stats in stats.items():
                comp_stats = dict([(self._form_key(stats_key, comp), stats_val) for stats_key, stats_val in
                                   comp_stats.items()])
                all_stats.update(comp_stats)
            if len(all_stats) > 0:
                self.send_data1(all_stats, duration)
        else:
            self.send_data2(stats, duration)

    def send_data1(self, stats, duration):
        stats_size = len(stats.keys())
        LOGGER.info('publish1, start = [%d]', stats_size)
        stats_item = stats.items()
        if stats_size > self.MAX_STATS_PER_POST:
            for index in range(0, stats_size, self.MAX_STATS_PER_POST):
                stats_chunk = dict(
                    item for item in stats_item[index:(index + self.MAX_STATS_PER_POST)])
                count, component = self._get_a_component(
                    self.NAME, stats_chunk, duration)
                components = list()
                components.append(component)
                self.post_data(components, count)
        else:
            components = list()
            count, component = self._get_a_component(
                self.NAME, stats, duration)
            components.append(component)
            self.post_data(components, count)
        LOGGER.info('publish1, end total count %d ', stats_size)

    def send_data2(self, stats, duration):
        LOGGER.info('publish2, start key count %d ', len(stats.values()))
        components = list()
        stats_count = 0
        stats_size = 0
        for device, dev_stats in stats.items():
            if len(dev_stats.items()) == 0:
                continue
            count, component = self._get_a_component(
                device, dev_stats, duration)
            stats_count += count
            stats_size += count
            components.append(component)
            if stats_size >= self.MAX_STATS_PER_POST:
                self.post_data(components, stats_size)
                stats_size = 0
                components = list()
        if len(components) > 0:
            self.post_data(components, stats_size)
        LOGGER.info('publish2, end stats_count count %d ', stats_count)

    @staticmethod
    def _form_key(component_key, device):
        keys = component_key.split('/')
        keys.insert(2, device)
        return '/'.join(keys)

    def _get_a_component(self, name, stats, duration):
        component = {'name': name,
                     'guid': self.UID,
                     'duration': duration,
                     'metrics': stats}

        return len(stats.keys()), component

    def post_data(self, components, stats_size):
        http_proxy = None
        if 'proxy' in self.config:
            http_proxy = {
                'http': self.config['proxy'],
                'https': self.config['proxy']}
        body = {'agent': {'host': socket.gethostname(),
                          'pid': os.getpid(),
                          'version': '1.0.0'},
                'components': components}
        http_headers = {'Accept': 'application/json',
                        'Content-Type': 'application/json',
                        'X-License-Key': self.config['license_key']}
        data = json.dumps(body, ensure_ascii=False)
        http_headers['Content-Encoding'] = 'deflate'
        level = (len(data) < 2000000) and 1 or 9
        data = zlib.compress(data, level)
        try:
            response = requests.post(self.URL,
                                     headers=http_headers,
                                     proxies=http_proxy,
                                     data=data,
                                     timeout=10,
                                     verify=True)
            LOGGER.info('post_data, code content and length [%s %r %d]',
                        response.status_code,
                        response.content.strip(), stats_size)
        except Exception as e:
            LOGGER.error('post_data, failed [%s]', e)
