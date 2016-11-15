# -*- coding: utf-8 -*-

import argparse, os, sys, time
from pysyslogclient import *

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Syslog client v%s" % (version))
	parser.add_argument("--server", "-s", type=str, help="Server name", required=True)
	parser.add_argument("--port", "-p", type=int, help="Port number", default=514)
	parser.add_argument("--protocol", "-t", choices=["tcp", "udp"], help="Used transprot protocol", default="udp")
	parser.add_argument("--rfc", "-r", choices=["5424", "3164"], help="RFC to use", default="5424")
	parser.add_argument("--program", "-o", type=str, help="Program name", default="SyslogClient")
	parser.add_argument("--pid", "-i", type=int, help="PID of program", default=os.getpid())
	parser.add_argument("--message", "-m", type=str, help="Message to send", required=True)
	args = parser.parse_args()

	if args.rfc == "5424":
		client = SyslogClientRFC5424(args.server, args.port, proto=args.protocol)
	else:
		client = SyslogClientRFC3164(args.server, args.port, proto=args.protocol)

	client.log(args.message, facility=FAC_SYSLOG, severity=SEV_DEBUG, program=args.program, pid=args.pid)

# vim: ft=python tabstop=2 shiftwidth=2 noexpandtab :
