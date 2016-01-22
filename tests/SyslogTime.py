#!/usr/bin/python3
# vim: noexpandtab tabstop=4 shiftwidth=4 fileformat=unix
# -*- coding: utf-8 -*-

import sys, datetime, time
import SyslogClient

def print_help():
	print("%s : {tcp|udp}://<SERVER>:<PORT> [rfc5434|rfc3164]" % (sys.argv[0]))
	sys.exit(0)

if __name__ == "__main__":
	host = "localhost"
	port = 514
	proto = "udp"
	rfc = "RFC3164"

	if len(sys.argv) == 1 or len(sys.argv) > 3:
		print_help()

	try:
		args1 = sys.argv[1].split("://")
		proto = args1[0]
		args2 = args1[1].split(":")
		host = args2[0]
		port = int(args2[1])

		if len(sys.argv) == 3:
			rfc = sys.argv[2]
			if rfc.upper() != "RFC3164" and rfc != "RFC5424":
				print_help()
		else:
			rfc = "RFC3164"

	except:
		print_help()
    
	if rfc == "RFC5424":
		client = SyslogClient.SyslogClientRFC5424(host, port, proto=proto)
	else:
		client = SyslogClient.SyslogClientRFC3164(host, port, proto=proto)

	while True:
		client.log(u"the time is %s" % (datetime.datetime.now()), facility=SyslogClient.FAC_SYSLOG, severity=SyslogClient.SEV_DEBUG)
		try:
			time.sleep(1)
		except KeyboardInterrupt as e:
			break


