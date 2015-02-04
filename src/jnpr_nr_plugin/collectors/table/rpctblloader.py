import os

import yaml
from jnpr.junos.factory import FactoryLoader


class MetaData(object):
    META_DATA = {}

    def keys(self):
        return self.META_DATA.keys()

    def values(self):
        return self.META_DATA.values()

    def items(self):
        return self.META_DATA.items()

    def get_values(self, find_key):
        return [
            value for key, value in self.META_DATA.items() if find_key in key]


def custom_loadyaml(path):
    if os.path.splitext(path)[1] == '':
        path += '.yml'
    stream = yaml.load(open(path, 'r'))
    return RPCFactoryLoader().load(stream)


class RPCFactoryLoader(FactoryLoader):
    def __init_(self):
        FactoryLoader.__init__(self)
        self.__catalog_dict = {}

    def __build_metadata(self, view_name):
        if view_name not in self.catalog:
            return

        view_dict = self.__catalog_dict[view_name]
        v_dict = [
            value for key,
            value in view_dict.items() if 'meta_data' in key]

        if len(v_dict) == 1 and isinstance(v_dict[0], dict):
            new_cls = type(view_name + '_MetaData', (MetaData,), {})
            new_cls.META_DATA = v_dict[0]
            self.catalog[view_name + 'MetaData'] = new_cls

    def load(self, catalog_dict, envrion={}):
        self.__catalog_dict = catalog_dict
        catalog = super(RPCFactoryLoader, self).load(catalog_dict)
        views = []
        for catalog_key, catalog_val in catalog_dict.items():
            if not ('rpc' in catalog_val or 'get' in catalog_val or 'view' in catalog_val):
                views.append(catalog_key)
        map(self.__build_metadata, views)
        return catalog
