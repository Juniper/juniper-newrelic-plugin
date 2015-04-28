import base64
from datetime import datetime
import os
import sys
import tempfile
import threading
import traceback
import zlib
import socket

from netaddr import iter_iprange
import netaddr

def decrypt_passwd(s):
    return zlib.decompress(base64.decodestring(s))

def get_host_name(ip):
    if not netaddr.valid_ipv4(ip):
        return ip
    try:
        qualified_name = socket.gethostbyaddr(ip)[0]
        if '.' in qualified_name:
            return qualified_name.split('.')[0]
        return qualified_name
    except:
        return ip

def get_str(val):
    if val is None:
        return ''
    return str(val)

def get_device_list(device_cfg):
    devices = list()
    for device in device_cfg:
        ip_address = device.get('ip_address')
        if '-' in ip_address or ',' in ip_address:
            if '-' in ip_address:
                ip_ranges = ip_address.split('-')
                if netaddr.valid_ipv4(ip_ranges[0]) and netaddr.valid_ipv4(ip_ranges[1]):
                    ip_list = list(
                        iter_iprange(
                            ip_ranges[0].strip(),
                            ip_ranges[1].strip()))
                else:
                    devices.append(device)
                    continue
            else:
                ip_list = ip_address.split(',')
            for ip in ip_list:
                new_device = device.copy()
                new_device['ip_address'] = str(ip)
                devices.append(new_device)
        else:
            devices.append(device)
    return devices

def dump_stack(signal, frame, log):
    try:
        id_name_map = dict([(threads.ident, threads.name)
                            for threads in threading.enumerate()])
        code = []
        for threadId, stack in sys._current_frames().items():
            code.append(
                "\n# Thread: %s(%d)" %
                (id_name_map.get(
                    threadId,
                    ""),
                 threadId))
            for filename, line_no, name, line in traceback.extract_stack(
                    stack):
                code.append(
                    'File: "%s", line %d, in %s' %
                    (filename, line_no, name))
                if line:
                    code.append("  %s" % (line.strip()))
        filename = "_".join(
            ['jnpr_plugin_stack', datetime.now().strftime("%y%m%d_%H%M%S")]) + '.txt'
        filename = tempfile.gettempdir() + os.sep + filename
        with open(filename, 'w') as f:
            f.write("\n ".join(code))
        log.critical('stack dumped to ' + filename)
        print 'stack dumped to ' + filename
    except Exception as e:
        log.exception('failed to dump stack [%s]', e)
