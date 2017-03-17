# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import pysyslogclient, sys

long_description=open("README", "r").read(4096)

setup(
	name="pysyslogclient",
	version=pysyslogclient.version,
	description='Syslog client implementation (RFC 3164/RFC 5424)',
	long_description=long_description,
	license='BSD-2-Clause',
	url="https://github.com/aboehm/pysyslogclient",
	
	author="Alexander Böhm",
	author_email="alxndr.boehm@gmail.com",

	classifiers = [
		'Development Status :: 5 - Production/Stable',

		'License :: OSI Approved :: BSD License',

		'Programming Language :: Python :: 3 :: Only',
		'Programming Language :: Python :: 3.5',
		'Programming Language :: Python :: 3.6',

		'Operating System :: Unix',
		'Operating System :: POSIX :: Linux',
		'Operating System :: Microsoft',

		'Topic :: System :: Logging',
		'Topic :: System :: Monitoring',
  ],

	packages=find_packages(),

	keywords="syslog logging monitoring",
)

# vim: ft=python tabstop=2 shiftwidth=2 noexpandtab :
