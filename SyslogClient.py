#!/usr/bin/python3
# vim: noexpandtab tabstop=4 shiftwidth=4 fileformat=unix
# -*- coding: utf-8 -*-

# Syslog client (RFC3164, RFC5424) for Python
#
# Copyright (c) 2016, Alexander Böhm
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
# 
# * Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# 	  SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

import sys, socket, datetime
import tzlocal

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

def datetime2rfc3339(dt):
	diff_sec = dt.tzinfo._utcoffset.seconds 
	diff_min = abs((diff_sec / 60) % 60)
	diff_hr = (diff_sec / 3600) % 60
	tz = ""

	if diff_hr == 0:
		tz = "Z"
	else:
		if diff_hr > 0:
			tz = "+%s" % (tz) 
	
		tz = "%s%.2d%.2d" % (tz, diff_hr, diff_min)

	return "%s%s" % (dt.strftime("%Y-%m-%dT%H:%M:%S.%f"), tz)

class SyslogClient:
	def __init__(self, server, port, proto='udp', forceipv4=False, clientname=None):
		self.server = server
		self.port = port
		self.proto = socket.SOCK_DGRAM
		self.socket = None
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

				except ConnectionRefusedError as e:
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
				self.socket.send(messagedata)
			except BrokenPipeError as e:
				self.close()

class SyslogClientRFC5424(SyslogClient):
	def __init__(self, server, port, proto='udp', forceipv4=False, clientname=None):
		SyslogClient.__init__(self, server, port, proto, forceipv4, clientname)

	def log(self, message, facility=None, severity=None, timestamp=None, hostname=None, version=1, appname=None, procid=None, msgid=None):

		if facility == None:
			facility = FAC_USER

		if severity == None:
			severity = SEV_INFO

		pri = facility*8 + severity

		if timestamp == None:
			t = datetime.datetime.now(tzlocal.get_localzone())
		else:
			t = timestamp

		if t.tzinfo == None:
			t = t.replace(tzinfo=tzlocal.get_localzone())
	
		timestamp_s = datetime2rfc3339(t)

		if hostname == None:
			hostname_s = self.clientname 
		else:
			hostname_s = hostname

		if appname == None:
			appname_s = "-" 
		else:
			appname_s = appname

		if procid == None:
			procid_s = "-"
		else:
			procid_s = procid

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
		SyslogClient.__init__(self, server, port, proto, forceipv4, clientname)

	def log(self, message, facility=None, severity=None, timestamp=None, hostname=None):
		if facility == None:
			facility = FAC_USER

		if severity == None:
			severity = SEV_INFO

		pri = facility*8 + severity

		if timestamp == None:
			t = datetime.datetime.now(tzlocal.get_localzone())
		else:
			t = timestamp

		if t.tzinfo == None:
			t = t.replace(tzinfo=tzlocal.get_localzone())
	
		timestamp_s = t.strftime("%b %d %H:%M:%S")

		if hostname == None:
			hostname_s = self.clientname 
		else:
			hostname_s = hostname

		d = "<%i>%s %s %s\n" % (
			pri,
			timestamp_s,
			hostname_s,
			message
		)

		self.send(d.encode('ASCII', 'ignore'))


