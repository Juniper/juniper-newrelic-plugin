from jnpr_nr_plugin.collectors.table import rpctblcollector
from jnpr_nr_plugin.collectors.table import rpctblcmds
from jnpr_nr_plugin.collectors import stores


class PortAndReStatsCollector(rpctblcollector.RPCTableCommandCollector):

    def __init__(self, config, device_mgr):
        super(
            PortAndReStatsCollector,
            self).__init__(config,
                           device_mgr)
        self.paths = list()

    def getcmds(self):
        cmds = list()
        cmds.append(
            rpctblcmds.RPCTableCommand(
                're',
                'jnpr_nr_plugin.collectors.table.port.restats',
                'REStats',
                None))
        cmds.append(
            rpctblcmds.RPCTableCommand(
                'interface',
                'jnpr_nr_plugin.collectors.table.port.portstats',
                'PortStats',
                None))
        return cmds

    def get_holder(
            self, device, key, r_key, col, c_metadata):
        c_name, c_val = col
        c_unit = c_metadata['unit']
        if c_name == 'used':
            c_val = 100 - int(c_val)
        c_type = c_metadata['type']
        c_key = '%s/%s/%s' % (key, c_name, r_key)
        if c_type == 'count':
            c_key = '%s/%s/%s' % (key, c_name, c_val)
        c_key = 'Component/%s[%s]' % (c_key, c_unit)
        holder = stores.StatsHolder(c_key, c_val, c_unit, c_type)
        summarize = 'summarize' in c_metadata and c_metadata.get('summarize', False)
        if summarize:
            path = 'Component/%s/%s/' % (key, c_name), '[%s]' % c_unit
            if path not in self.paths:
                self.paths.append(path)
        return holder

    def name(self):
        return 'jnpr_nr_plugin.collectors.table.port.portandrestats.PortAndReStatsCollector'

    def get_summary_paths(self):
        return self.paths
