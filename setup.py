import os

from setuptools import setup, find_packages


install_reqs = [
    'helper>=2.4.1',
    'requests>=2.4.1',
    'futures>=2.2.0',
    'junos-eznc==1.0.0']
base_path = '%s/jnpr_nr_plugin/etc' % os.getenv('VIRTUAL_ENV', '')
data_files = dict()
data_files[base_path] = ['LICENSE',
                         'readme.txt',
                         'etc/jnpr_nr_plugin/jnpr_nr_plugin.cfg',
                         'etc/init.d/jnpr_nr_plugin.rhel']

setup(
    name='jnpr_nr_plugin',
    version='1.0.0',
    author='juniper',
    author_email="jnpr-community-netdev@juniper.net",
    description=("Juniper's new relic plugin"),
    license="Apache 2.0",
    keywords="Juniper's new relic plugin",
    url="http://www.github.com/Juniper/jnpr_nr_plugin",
    package_dir={'': 'src'},
    platforms={'linux'},
    packages=find_packages('src'),
    package_data={
        'jnpr_nr_plugin.collectors.table.port.stats': ['*.yml']
    },
    data_files=[(key, data_files[key]) for key in data_files.keys()],
    entry_points={
        'console_scripts': ['jnpr_nr_plugin=jnpr_nr_plugin.main:main']},
    install_requires=install_reqs,
    classifiers=[
        'Intended Audience :: Network Administrators',
        'License :: OSI Approved :: Apache License',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2.7 :: Only',
        'Topic :: System :: Network Monitoring'
    ],
)
