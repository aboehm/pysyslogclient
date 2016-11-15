# -*- coding: utf-8 -*-

"""
pysyslogclient
--------------

Syslog client library for Python 2.7 / 3.x (UNIX/Windows) following

* RFC3164 (https://www.ietf.org/rfc/rfc3164.txt)
* RFC5424 (https://www.ietf.org/rfc/rfc5424.txt)

TCP and UDP as transport is possible. If TCP is used, on every log message,
that is send to the specified server, and a connection error occured, the
message will be dismissed and reconnect will be tried for the next message.

Usage
-----

A small CLI client is implemented in cli.py. To call it, run

	python -m pysyslogclient.cli

To setup the client for RFC 5424 over TCP to send to localhost on port 514:

	>>> from pysyslogclient import *
	>>> client = SyslogClientRFC5424("localhost", 514, proto="TCP")

or for RFC 3164:

	>>> client = SyslogClientRFC3164("localhost", 514, proto="TCP")

Log the message "Hello syslog server" with standard severity **INFO** as facility
**USER**. As program name **SyslogClient** the PID of the called python interpreter
is used.

	>>> client.log("Hello syslog server")

To specify more options, call log with more arguments. For example to log a
the message as program **Logger** with PID **1** as facility **SYSTEM** with severity
**EMERGENCY**, call log the following way:

	>>> client.log("Hello syslog server", facility=FAC_SYSTEM, severity=SEV_EMERGENCY, program="Logger", pid=1)

To disconnect the client, call

	>>> client.close()

Author
------

* Alexander Böhm (alxndr.boehm@gmail.com)


License
-------

BSD 2-Clause

Repository
----------

* https://github.com/aboehm/pysyslogclient

"""

version = "0.1.0"

import socket, sys
from datetime import datetime

def datetime2rfc3339(dt, is_utc=False):
	if is_utc == False:
		# calculating timezone
		d1 = datetime.now()
		d2 = datetime.utcnow()
		diff_hr = (d1-d2).seconds/60/60
		tz = ""

		if diff_hr == 0:
			tz = "Z"
		else:
			if diff_hr > 0:
				tz = "+%s" % (tz) 
		
			tz = "%s%.2d%.2d" % (tz, diff_hr, 0)

		return "%s%s" % (dt.strftime("%Y-%m-%dT%H:%M:%S.%f"), tz)

	else:
		return dt.isoformat()+'Z'

FAC_KERNEL = 0
FAC_USER = 1
FAC_MAIL = 2
FAC_SYSTEM = 3
FAC_SECURITY = 4
FAC_SYSLOG = 5
FAC_PRINTER = 6
FAC_NETWORK = 7
FAC_UUCP = 8
FAC_CLOCK = 9
FAC_AUTH = 10
FAC_FTP = 11
FAC_NTP = 12
FAC_LOG_AUDIT = 13
FAC_LOG_ALERT = 14
FAC_CLOCK2 = 15
FAC_LOCAL0 = 16
FAC_LOCAL1 = 17
FAC_LOCAL2 = 18
FAC_LOCAL3 = 19
FAC_LOCAL4 = 20
FAC_LOCAL5 = 21
FAC_LOCAL6 = 22
FAC_LOCAL7 = 23

SEV_EMERGENCY = 0
SEV_ALERT = 1
SEV_CRITICAL = 2
SEV_ERROR = 3
SEV_WARNING = 4
SEV_NOTICE = 5
SEV_INFO = 6
SEV_DEBUG = 7

class SyslogClient(object):
	def __init__(self, server, port, proto='udp', forceipv4=False, clientname=None, rfc=None, maxMessageLength=1024):
		self.socket = None
		self.server = server
		self.port = port
		self.proto = socket.SOCK_DGRAM
		self.rfc = rfc
		self.maxMessageLength = maxMessageLength
		self.forceipv4 = forceipv4

		if proto != None:
			if proto.upper() == 'UDP':
				self.proto = socket.SOCK_DGRAM
			elif proto.upper() == 'TCP':
				self.proto = socket.SOCK_STREAM

		if clientname == None:
			self.clientname = socket.getfqdn()
			if self.clientname == None:
				self.clientname = socket.gethostname()

	def connect(self):
		if self.socket == None:
			r = socket.getaddrinfo(self.server, self.port, socket.AF_UNSPEC, self.proto) 
			if r == None:
				return False
			
			for (addr_fam, sock_kind, proto, ca_name, sock_addr) in r:
				self.socket = socket.socket(addr_fam, self.proto)
				if self.socket == None:
					return False

				try:
					self.socket.connect(sock_addr)
					return True

				except socket.timeout as e:
					if self.socket != None:
						self.socket.close()
						self.socket = None
					continue

				# ensure python 2.x compatibility
				except socket.error as e:
					if self.socket != None:
						self.socket.close()
						self.socket = None
					continue

			return False

		else:
			return True

	def close(self):
		if self.socket != None:
			self.socket.close()
			self.socket = None

	def log(self, message, timestamp=None, hostname=None, facility=None, severity=None):
		pass

	def send(self, messagedata):
		if self.socket != None or self.connect():
			try:
				if self.maxMessageLength != None:
					self.socket.send(messagedata[:self.maxMessageLength])
				else:
					self.socket.send(messagedata)
			except IOError as e:
				self.close()

class SyslogClientRFC5424(SyslogClient):
	def __init__(self, server, port, proto='udp', forceipv4=False, clientname=None):
		SyslogClient.__init__(self,
			server=server,
			port=port,
			proto=proto,
			forceipv4=forceipv4,
			clientname=clientname,
			rfc='5424',
			maxMessageLength=None,
		)

	def log(self, message, facility=None, severity=None, timestamp=None, hostname=None, version=1, program=None, pid=None, msgid=None):
		if facility == None:
			facility = FAC_USER

		if severity == None:
			severity = SEV_INFO

		pri = facility*8 + severity

		if timestamp == None:
			timestamp_s = datetime2rfc3339(datetime.utcnow(), is_utc=True)
		else:
			timestamp_s = datetime2rfc3339(timestamp, is_utc=False)

		if hostname == None:
			hostname_s = self.clientname 
		else:
			hostname_s = hostname

		if program == None:
			appname_s = "-" 
		else:
			appname_s = program

		if pid == None:
			procid_s = "-"
		else:
			procid_s = pid

		if msgid == None:
			msgid_s = "-"
		else:
			msgid_s = msgid

		d = "<%i>%i %s %s %s %s %s %s\n" % (
			pri,
			version,
			timestamp_s,
			hostname_s,
			appname_s,
			procid_s,
			msgid_s,
			message
		)

		self.send(d.encode('utf-8'))

class SyslogClientRFC3164(SyslogClient):
	def __init__(self, server, port, proto='udp', forceipv4=False, clientname=None):
		SyslogClient.__init__(self,
			server=server,
			port=port,
			proto=proto,
			forceipv4=forceipv4,
			clientname=clientname,
			rfc='3164',
			maxMessageLength=1024,
		)

	def log(self, message, facility=None, severity=None, timestamp=None, hostname=None, program="SyslogClient", pid=None):
		if facility == None:
			facility = FAC_USER

		if severity == None:
			severity = SEV_INFO

		pri = facility*8 + severity

		if timestamp == None:
			t = datetime.now()
		else:
			t = timestamp
	
		timestamp_s = t.strftime("%b %d %H:%M:%S")

		if hostname == None:
			hostname_s = self.clientname 
		else:
			hostname_s = hostname

		tag_s = ""
		if program == None:
			tag_s += "SyslogClient"
		else:
			tag_s += program

		if pid != None:
			tag_s += "[%i]" % (pid)

		d = "<%i>%s %s %s: %s\n" % (
			pri,
			timestamp_s,
			hostname_s,
			tag_s,
			message
		)

		self.send(d.encode('ASCII', 'ignore'))

if __name__ == '__main__':
	import doctest
	doctest.testmod()

# vim: ft=python tabstop=2 shiftwidth=2 noexpandtab :
