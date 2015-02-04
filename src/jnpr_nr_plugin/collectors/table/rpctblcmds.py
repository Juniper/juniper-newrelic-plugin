from jnpr_nr_plugin.collectors import cmds


class RPCTableCommand(cmds.Command):
    def __init__(self, name, module, cls, fltr):
        super(
            RPCTableCommand,
            self).__init__(
            name)
        self.module = module
        self.cls = cls
        self.filter = fltr


class RPCTableCommandResult(cmds.CommandResult):
    def __init__(self, name, result=None, metadata=None):
        super(
            RPCTableCommandResult,
            self).__init__(name, result)
        self.metadata = metadata
