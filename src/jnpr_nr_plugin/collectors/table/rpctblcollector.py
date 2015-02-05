import logging
import importlib

from jnpr_nr_plugin.collectors import collector
import rpctblcmds


LOGGER = logging.getLogger(__name__)


class RPCTableCommandCollector(collector.StatsCollector):
    def __init__(self, config, device_mgr):
        super(
            RPCTableCommandCollector,
            self).__init__(config,
                           device_mgr)

    def processcmd(self, device, cmd_response):
        table = cmd_response
        LOGGER.debug('process_cmd, [%s, %s]', device, table.name)
        if table.result is None or table.result.keys(
        ) is None or table.metadata is None:
            LOGGER.warn(
                'process_cmd, for device, no data obtained for the poll [%s, %s]',
                device, table.name)
            return
        try:
            for r_key, row in table.result.items():
                if r_key.isdigit():
                    r_key = table.name + r_key
                r_key = r_key.replace('/', '-').strip()
                for col in row:
                    c_name, c_val = col
                    if c_name is None or c_val is None:
                        LOGGER.warn(
                            'process_cmd, for device, table, key, name'
                            ' [%s, %s, %s, %s] value is none ', device, table.name,
                            r_key,
                            c_name)
                        continue
                    c_metadata = table.metadata.get_values(c_name)
                    if c_metadata and len(c_metadata) == 1:
                        self.update_stats(device, self.get_holder(device, table.name, r_key, col, c_metadata[0]))
            self.summarize(device, self.get_summary_paths())
        except Exception as e:
            LOGGER.exception(
                'process_cmd, for device, table [%s, %s, %s] failed',
                device,
                table.name,
                e)
        LOGGER.info('process_cmd, for device, table = size [%s, %s = %d]', device, table.name,
                    len(table.result.items()))

    def executecmd(self, device, dev_obj, cmd):
        name = cmd.name
        LOGGER.debug('execute_cmd, [%s, %s]', device, name)
        try:
            tbl_mdl_cls = importlib.import_module(
                cmd.module)
            table = getattr(tbl_mdl_cls,
                            cmd.cls)(dev_obj)
            if cmd.filter:
                table = table.get(cmd.filters)
            else:
                table = table.get()
            tbl_metadata = getattr(
                tbl_mdl_cls,
                table.VIEW.__name__ +
                'MetaData')
            return rpctblcmds.RPCTableCommandResult(
                cmd.name, table, tbl_metadata())
        except Exception as e:
            LOGGER.exception('execute_cmd,for device, table failed  [%s, %s %s]', device,
                             cmd.name, e)
            return rpctblcmds.RPCTableCommandResult(name)

    def get_summary_paths(self):
        raise NotImplementedError

    def get_holder(
            self, device, key, r_key, col, c_metadata):
        return NotImplementedError
