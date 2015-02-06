==============
jnpr_nr_plugin
==============
The Juniper plugin for New Relic collects metrics from Juniper devices such as the EX-Series and QFX-Series switches and the MX-Series routers. The collected metrics include routing engine statistics (for instance memory and CPU used) and physical interface statistics (for instance input/output pps, input/output unicast multicast and broadcast pps). The plugin sends the collected metrics up to the New Relic cloud using JSON over HTTPS.

The plugin uses NETCONF to communicate with the Juniper devices. For more information on NETCONF see http://www.juniper.net/documentation/en_US/junos13.2/information-products/pathway-pages/netconf-guide/netconf.html.  Internally it uses the open source Py-Junos-Eznc library which provides a high-level abstraction of the NETCONF interface.  For more information on Py-Junos-Eznc see https://github.com/Juniper/py-junos-eznc

The plugin supports PIP installation. For documentation on installation see installation.txt. It is very easy to get the plugin up and running, using a simple configuration that includes New Relic license key, the device credentials, and the poll time. For example configuration file see etc/jnpr_nr_plugin/jnpr_nr_plugin.cfg. 

As soon as it starts reporting device metrics to the New Relic analytics platform, the user can login to his or her New Relic account to view the reported metrics

support group:  juniper-newRelicPlugin-support@juniper.net
