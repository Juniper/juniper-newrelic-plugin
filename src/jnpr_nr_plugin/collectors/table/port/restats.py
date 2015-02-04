from os.path import splitext

from jnpr_nr_plugin.collectors.table import rpctblloader


_YAML_ = splitext(__file__)[0] + '.yml'
globals().update(rpctblloader.custom_loadyaml(_YAML_))
