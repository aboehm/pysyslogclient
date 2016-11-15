# pysyslogclient

Syslog client for python (RFC3164/5424) for UNIX and Windows

## Description

Syslog client following

* RFC3164 (https://www.ietf.org/rfc/rfc3164.txt)
* RFC5424 (https://www.ietf.org/rfc/rfc5424.txt)

with UNIX and Windows support. TCP and UDP transport is possible.

If TCP is used, on every log message, that is send to the specified server,
and a connection error occured, the message will be dismissed and
a reconnect will be tried for the next message.

## Usage

A small CLI client is implemented in *client.py*. To call it, run

```
python -m SyslogClient.client
```

### Startup client 

To setup the client for RFC5424 over TCP to send to SERVER:PORT:

```
import SyslogClient
client = SyslogClient.SyslogClientRFC5424(SERVER, PORT, proto="TCP")
```

or for RFC3164:

```
import SyslogClient
client = SyslogClient.SyslogClientRFC3164(SERVER, PORT, proto="TCP")
```

### Log a messsage

Log the message "Hello syslog server" with standard severity *INFO* as facility
*USER*. As program name *SyslogClient* the PID of the called python interpreter
is used.

```
client.log("Hello syslog server")

```

To specify more options, call log with more arguments. For example to log a
the message as program *Logger* with PID *1* as facility *SYSTEM* with severity
*EMERGENCY*, call log the following way:

```
client.log("Hello syslog server",
	facility=SyslogClient.FAC_SYSTEM,
	severity=SyslogClient.SEV_EMERGENCY,
	program="Logger",
	pid=1)
```

### Shutdown

To disconnect, call

```
client.close()
```

